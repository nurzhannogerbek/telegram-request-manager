from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.validation import Validation

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
        await self.bot.send_message(chat_id=user_id, text=self.localization.get_multilang_welcome_message(),
                                    reply_markup=InlineKeyboardMarkup(keyboard))

    async def set_language(self, update, context):
        """
        Handles the language selection callback and stores the user's language preference.

        Args:
            update (Update): The incoming callback update.
            context (CallbackContext): The context of the update.
        """
        query = update.callback_query
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
        Handles the user's response to the privacy policy and initiates the questionnaire if accepted.

        Args:
            update (Update): The incoming callback update.
            context (CallbackContext): The context of the update.
        """
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        lang, current_question_index, responses, chat_id = self.google_sheets.get_user_state(user_id)
        if isinstance(responses, dict):
            responses = [(k, v) for k, v in responses.items()]

        if query.data == "privacy_accept":
            # Start the questionnaire if the user accepts the privacy policy.
            form = ApplicationForm(lang, self.localization)
            form.current_question_index = 0
            form.responses = responses
            self.user_forms[user_id] = form
            self._save_user_state(user_id, lang, form.current_question_index, form.responses, chat_id)
            await query.edit_message_text(text=self.localization.get_string(lang, "start_questionnaire"))
            await self._send_next_question(user_id)
        else:
            # Inform the user that the interaction has ended if they decline the privacy policy.
            # await query.edit_message_text(text=self.localization.get_string(lang, "decline_message"))
            pass

    async def handle_response(self, update, context):
        """
        Handles any incoming text messages from the user in order to proceed with or initialize the questionnaire.
        It verifies whether the user has selected a language and agreed to the privacy policy (if required).
        If these preconditions are not met, the user is prompted accordingly.

        Args:
            update (Update): The incoming Telegram update that contains the user's text message.
            context (CallbackContext): Provides context for the Telegram bot, including user data.
        """
        # Extract the Telegram user ID from the incoming message.
        user_id = update.message.from_user.id

        # Retrieve the user's state from our persistent storage, such as Google Sheets or a database.
        lang, current_question_index, responses, chat_id = self.google_sheets.get_user_state(user_id)

        # If the user has not chosen a language yet (lang is None or an empty string).
        # In this case, we send a message in three languages, instructing them to press a button.
        if not lang:
            # Send a multilingual prompt instructing the user to press one of the buttons.
            await update.message.reply_text(Localization.PRESS_BUTTON_MULTILANG)
            return

        # If the user has chosen a language but has not yet agreed to the privacy policy (current_question_index < 0).
        # We prompt them in the chosen language to press the button on the screen.
        if current_question_index < 0:
            press_button_text = self.localization.get_string(lang, "press_button")
            # Notify the user that they should press the "Agree" or "Disagree" button to proceed.
            await update.message.reply_text(press_button_text)
            return

        # If we reach this point, current_question_index >= 0, meaning the user has agreed to the privacy policy.
        # We can safely proceed with the questionnaire flow.
        if isinstance(responses, dict):
            # Convert responses from a dict to a list of tuples if necessary.
            responses = [(q, a) for q, a in responses.items()]

        # Retrieve or create an in-memory form object for the user.
        form = self.user_forms.get(user_id)
        if not form:
            # If no form exists in memory, reconstruct it from the persisted data.
            form = ApplicationForm(lang, self.localization)
            form.current_question_index = current_question_index
            form.responses = responses
            self.user_forms[user_id] = form

        # Extract the user's textual response from the message.
        user_response = update.message.text.strip()

        # Validate the user's response based on the current question's type (email, phone, age, etc.).
        # If validation fails, _validate_and_handle_response will notify the user and return False.
        if not await self._validate_and_handle_response(user_response, form, user_id):
            return

        # Check if the form is complete (all questions answered).
        if form.is_complete():
            # Save final user data to Google Sheets or another storage.
            self.google_sheets.save_to_sheet(user_id, form.get_all_responses())
            # Update the user's state to reflect the completed questionnaire.
            self._save_user_state(user_id, form.lang, form.current_question_index, form.responses, chat_id)
            # Remove the form from memory to free resources.
            del self.user_forms[user_id]
            # Notify the user that the application is complete.
            await update.message.reply_text(self.localization.get_string(form.lang, "application_complete"))
            # Optionally approve the user's request to join a group, if applicable.
            await self.approve_join_request(user_id, context)
        else:
            # If the form is not complete, send the next question to the user.
            await self._send_next_question(user_id)

    async def handle_join_request(self, update, context):
        """
        Handles join requests to the group by initializing the user's state and starting the interaction.

        Args:
            update (Update): The incoming join request update.
            context (CallbackContext): The context of the update.
        """
        join_request = update.chat_join_request
        user_id = join_request.from_user.id
        chat_id = join_request.chat.id
        # Save the initial user state with an empty language and no responses.
        self._save_user_state(user_id, "", 0, [], str(chat_id))
        await self.start(update, context)

    async def approve_join_request(self, user_id, context):
        """
        Approves the user's join request after successful completion of the questionnaire.

        Args:
            user_id (str): The Telegram user ID.
            context (CallbackContext): The context of the update.
        """
        _, _, _, chat_id = self.google_sheets.get_user_state(user_id)
        if chat_id:
            # Approve the join request using the chat ID and user ID.
            await context.bot.approve_chat_join_request(chat_id=int(chat_id), user_id=user_id)
            self.utils.notify_admin(f"✅ User {user_id} has been approved.")

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
