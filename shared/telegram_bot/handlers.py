from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.validation import Validation
from telegram.error import Forbidden
from shared.telegram_bot.logger import logger
from shared.telegram_bot.config import Config

class BotHandlers:
    """
    Defines handlers for various Telegram bot events, including commands, messages, and callbacks.
    Manages user interactions, questionnaire progress, and join requests.
    """

    def __init__(self, google_sheets, utils, bot):
        """
        Initializes the BotHandlers instance with dependencies for managing state and communication.

        Args:
            google_sheets (GoogleSheets): Instance for managing Google Sheets interactions.
            utils (Utils): Utility instance for sending notifications and messages.
            bot (Bot): The Telegram bot instance.
        """
        self.google_sheets = google_sheets
        self.utils = utils
        self.bot = bot
        self.user_forms = {}  # Dictionary to track user forms.
        self.localization = Localization()  # Localization instance to retrieve strings.

    async def start(self, update, context):
        """
        Handles the /start command by sending a language selection menu to the user.

        Args:
            update (Update): The incoming update triggering the command.
            context (CallbackContext): The context of the update.
        """
        user_id = update.effective_user.id
        # Create the language selection menu with buttons.
        keyboard = [[
            InlineKeyboardButton("Русский", callback_data="lang_ru"),
            InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
            InlineKeyboardButton("English", callback_data="lang_en")
        ]]
        await self.bot.send_message(
            chat_id=user_id,
            text=self.localization.get_multilang_welcome_message(),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def set_language(self, update, context):
        """
        Handles the language selection callback and stores the user's language preference.

        Args:
            update (Update): The incoming callback update.
            context (CallbackContext): The context of the update.
        """
        query = update.callback_query
        user = query.from_user
        if user.is_bot:
            return
        await query.answer()
        user_id = query.from_user.id
        lang = query.data.split("_")[1]  # Extract the selected language code.
        context.user_data["lang"] = lang
        chat_id = self.google_sheets.get_chat_id(user_id)
        # Save the user's state with the selected language.
        self._save_user_state(user_id, lang, -1, [], chat_id)
        await self.send_privacy_policy(update, context)

    async def send_privacy_policy(self, update, context):
        """
        Sends the privacy policy to the user in the selected language.

        Args:
            update (Update): The incoming update.
            context (CallbackContext): The context of the update.
        """
        user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
        lang = context.user_data.get("lang") or self.google_sheets.get_user_state(user_id)[0]
        privacy_policy_link = self.utils.fetch_privacy_policy(lang, self.localization)
        message_text = f"{self.localization.get_string(lang, 'privacy_prompt')}\n\n{privacy_policy_link}"
        keyboard = [[
            InlineKeyboardButton(self.localization.get_string(lang, "privacy_accept"), callback_data="privacy_accept"),
            # InlineKeyboardButton(self.localization.get_string(lang, "privacy_decline"), callback_data="privacy_decline")
        ]]
        if update.callback_query:
            # Edit the existing message to include the privacy policy.
            await update.callback_query.edit_message_text(
                text=message_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            # Send a new message with the privacy policy.
            await self.bot.send_message(
                chat_id=user_id,
                text=message_text,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )

    async def handle_privacy_response(self, update, context):
        """
        Handles the user's response to the privacy policy agreement.
        If the user agrees, the bot starts the questionnaire by sending the first question.

        Args:
            update (Update): The incoming callback update from Telegram.
            context (CallbackContext): The context of the update.
        """
        # Get the callback query from the user.
        query = update.callback_query
        user = query.from_user

        # Ignore callbacks from bots to prevent unwanted processing and Forbidden errors.
        if user.is_bot:
            return

        await query.answer()  # Acknowledge the callback to prevent Telegram from showing "loading...".

        # Extract the user's Telegram ID.
        user_id = user.id

        # Retrieve the user's saved state from Google Sheets.
        lang, current_question_index, responses, chat_id = self.google_sheets.get_user_state(user_id)

        # Convert responses from dictionary to list of tuples if necessary.
        if isinstance(responses, dict):
            responses = [(k, v) for k, v in responses.items()]

        # Check if the user accepted the privacy policy.
        if query.data == "privacy_accept":
            # Create a new application form for the user to start the questionnaire.
            form = ApplicationForm(lang, self.localization)
            form.current_question_index = 0  # Set the starting question index.
            form.responses = responses  # Load any existing responses.
            self.user_forms[user_id] = form  # Store the form in memory.

            # Save the user's state (so progress can be recovered if needed).
            self._save_user_state(user_id, lang, form.current_question_index, form.responses, chat_id)

            # Retrieve the first question from the questionnaire.
            first_question = form.get_next_question()

            # Edit the existing message to include the questionnaire introduction and the first question.
            await query.edit_message_text(
                text=f"{self.localization.get_string(lang, 'start_questionnaire')}\n\n{first_question}"
            )

        # If the user had rejected the policy (not used in current implementation).
        else:
            # The bot does nothing; you may customize this behavior if needed.
            pass

    async def handle_response(self, update, context):
        """
        Handles any incoming text messages from the user in order to proceed with or initialize the questionnaire.
        It verifies whether the user has selected a language and agreed to the privacy policy (if required).
        If these preconditions are not met, the user is prompted accordingly.

        Args:
            update (Update): The incoming Telegram update containing the user's text message.
            context (CallbackContext): Provides context for the Telegram bot, including user data.
        """
        # 1. Ensure the update contains a message and a real user (not a bot).
        if not update.message or update.message.chat.type != "private" or not update.message.from_user:
            return  # Ignore updates without a message or a user.

        # Extract the user object from the message for further validation and processing.
        user = update.message.from_user

        # 2. Skip if the message is from a bot account.
        if not user or user.is_bot:
            return

        # 3. Extract the user's Telegram ID (used for private messaging).
        user_id = user.id

        # 4. Retrieve the user's state (language, current question index, responses, and group chat_id).
        lang, current_question_index, responses, stored_chat_id = self.google_sheets.get_user_state(user_id)

        # 5. If the user has not selected a language yet, prompt them to choose one.
        if not lang:
            # Always reply in private chat, even if the user mistakenly messages in the group.
            try:
                await context.bot.send_message(chat_id=user_id, text=Localization.PRESS_BUTTON_MULTILANG)
            except Forbidden:
                logger.warning(f"Cannot send message to user {user_id} — bot is not allowed to initiate the chat.")
            return

        # 6. If the user has selected a language but hasn't agreed to the privacy policy yet, prompt them.
        if current_question_index < 0:
            press_button_text = self.localization.get_string(lang, "press_button")
            await context.bot.send_message(chat_id=user_id, text=press_button_text)
            return

        # 7. Convert responses from a dictionary to a list of tuples if necessary.
        if isinstance(responses, dict):
            responses = [(q, a) for q, a in responses.items()]

        # 8. Retrieve or create an in-memory ApplicationForm object for the user.
        form = self.user_forms.get(user_id)
        if not form:
            form = ApplicationForm(lang, self.localization)
            form.current_question_index = current_question_index
            form.responses = responses
            self.user_forms[user_id] = form

        # Skip saving if the form is already complete.
        if form.is_complete():
            return

        # 9. Extract the user's response text and validate it.
        user_response = update.message.text.strip()
        if not await self._validate_and_handle_response(user_response, form, user_id):
            return  # If validation fails, stop processing further.

        # 10. Check if the form is complete.
        if form.is_complete():
            # 10.1 Gather all user responses into a dictionary.
            final_answers = form.get_all_responses()

            # 10.2 Fetch username and bio from Telegram API (only works if the bot is an admin).
            chat_info = await context.bot.get_chat(user_id)
            username = chat_info.username or ""
            bio = chat_info.bio or ""

            # 10.3 Add the username and bio to the final_answers dictionary.
            final_answers["Username"] = username
            final_answers["Bio"] = bio

            # 10.4 Save the user's responses in Google Sheets.
            self.google_sheets.save_to_sheet(user_id, final_answers)

            # 10.5 Cleanup and confirm completion.
            del self.user_forms[user_id]
            self._save_user_state(user_id, form.lang, form.current_question_index, form.responses, stored_chat_id)

            # 10.6 Build and send a localized confirmation message to the user.
            completion_text = self.localization.get_string(form.lang, "application_complete")

            # Append the group invite link if it’s available in environment variables.
            if Config.GROUP_INVITE_LINK:
                # Optionally format as Markdown clickable link.
                completion_text += f"\n\n🔗 [Qazaq IT Community]({Config.GROUP_INVITE_LINK})"

            # Send the message using Markdown for better formatting.
            await context.bot.send_message(chat_id=user_id, text=completion_text, parse_mode="Markdown")

            # 10.7 Approve the user’s request to join the group (if applicable).
            await self.approve_join_request(user_id, context)
        else:
            # 11. If the form is not yet complete, send the next question to the user.
            await self._send_next_question(user_id)

    async def handle_join_request(self, update, context):
        """
        Handles join requests to the group by initializing the user's state and starting the interaction.

        Args:
            update (Update): The incoming join request update from Telegram.
            context (CallbackContext): The context associated with the update.
        """
        # Extract the join request object from the update.
        join_request = update.chat_join_request

        # Extract the user who sent the join request.
        user = join_request.from_user

        # Ignore the request if it's coming from another bot (Telegram bots can't interact with each other).
        if user.is_bot:
            return  # Skip processing join requests from bots.

        # Get the unique Telegram user ID of the user requesting to join.
        user_id = user.id

        # Get the chat ID of the group the user is requesting to join.
        chat_id = join_request.chat.id

        # Initialize and save the user's state in Google Sheets with:
        # - an empty language string (to be selected later),
        # - starting at question index 0,
        # - an empty list of responses,
        # - and the group chat ID as a string.
        self._save_user_state(user_id, "", 0, [], str(chat_id))

        # Start the onboarding process by sending a language selection message.
        await self.start(update, context)

    async def approve_join_request(self, user_id, context):
        """
        Approves the user's join request after successful completion of the questionnaire
        and sends full user data to the admin group.

        Args:
            user_id (str): The Telegram user ID.
            context (CallbackContext): The context of the update.
        """
        # Retrieve user's saved state (includes chat_id).
        lang, _, _, chat_id = self.google_sheets.get_user_state(user_id)

        # Approve the join request.
        if not chat_id:
            chat_id = Config.DEFAULT_GROUP_CHAT_ID
        if chat_id:
            await context.bot.approve_chat_join_request(chat_id=int(chat_id), user_id=user_id)

        # Fetch the full row of data from Google Sheets by user ID.
        final_data = self.google_sheets.get_user_row(user_id)
        if not final_data:
            await self.utils.notify_admin("✅ User approved but no data found in the Google Sheets.")
            return

        # Format the data for a readable admin message.
        formatted_message = "✅ *New Member Approved!*\n\n"
        for key, value in final_data.items():
            formatted_message += f"*{key}:* {value}\n"

        # Send to admin group.
        await self.utils.notify_admin(formatted_message)

    @staticmethod
    async def fetch_username_and_bio(context, user_id):
        """
        Asynchronously fetches the user's chat info from the Telegram API (get_chat).
        Returns the username and bio if available; otherwise returns empty strings.

        Args:
            context (CallbackContext): The context of the current update, used to access bot methods.
            user_id (int): The Telegram user ID for which we want to retrieve info.

        Returns:
            tuple(str, str): A tuple (username, bio).
        """
        # Since the bot is an admin, get_chat should provide username and bio if they're set.
        chat_info = await context.bot.get_chat(user_id)

        # Extract username and bio, defaulting to empty strings if they're None.
        username = chat_info.username or ""
        bio = chat_info.bio or ""

        return username, bio

    def setup(self, application):
        """
        Sets up the handlers for the Telegram bot by registering them with the application.

        Args:
            application (Application): The Telegram bot application.
        """
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_privacy_response, pattern="^privacy_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        application.add_handler(ChatJoinRequestHandler(self.handle_join_request))

    def _save_user_state(self, user_id, lang, current_question_index, responses, chat_id):
        """
        Saves the user's current state to Google Sheets.

        Args:
            user_id (str): The Telegram user ID.
            lang (str): The selected language.
            current_question_index (int): The index of the current question.
            responses (list): The list of question-response pairs.
            chat_id (str): The Telegram chat ID.
        """
        if not chat_id:
            chat_id = Config.DEFAULT_GROUP_CHAT_ID
        self.google_sheets.save_user_state(user_id, lang, current_question_index, responses, chat_id)

    async def _send_next_question(self, user_id):
        """
        Sends the next question in the questionnaire to the user.

        Args:
            user_id (str): The Telegram user ID.
        """
        form = self.user_forms.get(user_id)
        next_question = form.get_next_question() if form else None
        if next_question:
            self._save_user_state(user_id, form.lang, form.current_question_index, form.responses,
                                  self.google_sheets.get_chat_id(user_id))
            await self.bot.send_message(chat_id=user_id, text=next_question)

    async def _validate_and_handle_response(self, user_response, form, user_id):
        """
        Validates the user's response based on the current question type and saves it if valid.

        Args:
            user_response (str): The user's response.
            form (ApplicationForm): The form instance tracking the user's progress.
            user_id (str): The Telegram user ID.

        Returns:
            bool: True if the response is valid and saved, False otherwise.
        """
        current_question_type = form.get_current_question_type()
        # Validate based on the question type.
        if current_question_type == "email" and not Validation.validate_email(user_response):
            await self.bot.send_message(chat_id=user_id, text=self.localization.get_string(form.lang, "invalid_email"))
            return False
        if current_question_type == "phone" and not Validation.validate_phone(user_response):
            await self.bot.send_message(chat_id=user_id, text=self.localization.get_string(form.lang, "invalid_phone"))
            return False
        if current_question_type == "age" and not Validation.validate_age(user_response):
            await self.bot.send_message(chat_id=user_id, text=self.localization.get_string(form.lang, "invalid_age"))
            return False
        # Save the valid response and advance to the next question.
        form.save_response(user_response)
        return True
