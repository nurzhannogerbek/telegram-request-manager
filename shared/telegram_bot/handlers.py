from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.validation import Validation
from shared.telegram_bot.utils import Utils

class BotHandlers:
    """
    Class to manage bot commands, messages, and user interactions, including the application form flow.
    """

    def __init__(self):
        """
        Initializes the bot handlers with the necessary components, including localization,
        Google Sheets integration, and user-specific application forms.
        """
        self.user_forms = {}  # Dictionary to store active forms keyed by user ID.
        self.localization = Localization()  # Handles localization for strings and questions.
        self.google_sheets = GoogleSheets()  # Manages interactions with Google Sheets.
        self.utils = Utils()  # Utility functions for admin notifications and other tasks.

    async def start(self, update, context):
        """
        Handles the /start command to display a welcome message with language options.

        :param update: The Telegram update object containing information about the incoming message.
        :param context: The context object to store user-specific data and other session-related information.
        """
        try:
            user_id = update.effective_user.id
            print(f"User {user_id} issued the /start command.")

            # Display language options as inline buttons.
            keyboard = [
                [
                    InlineKeyboardButton("Русский", callback_data="lang_ru"),
                    InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
                    InlineKeyboardButton("English", callback_data="lang_en")
                ]
            ]

            # Send the welcome message with the language selection buttons.
            await context.bot.send_message(
                chat_id=user_id,
                text=self.localization.get_multilang_welcome_message(),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            print(f"Error in start handler: {e}")

    async def set_language(self, update, context):
        """
        Handles the language selection and stores it in the context.
        Sends the privacy policy in the selected language and saves the user state.
        """
        query = update.callback_query  # Get callback query.
        await query.answer()  # Acknowledge the query.

        try:
            user_id = query.from_user.id  # Get user ID.
            lang = query.data.split("_")[1]  # Extract the selected language code.

            print(f"User {user_id} selected language: {lang}.")
            context.user_data["lang"] = lang  # Store language in context.

            # Initialize the form state with default values (no responses and question index 0).
            initial_question_index = 0
            initial_responses = {}

            # Save the user's state immediately.
            self.google_sheets.save_user_state(user_id, lang, initial_question_index, initial_responses)

            # Send the privacy policy using the chosen language.
            await self.send_privacy_policy(update, context)
        except Exception as e:
            print(f"Error in set_language handler: {e}")

    async def send_privacy_policy(self, update, context):
        """
        Sends the privacy policy link in the user's selected language and prompts for consent.

        :param update: The Telegram update object containing the callback query or message.
        :param context: The context object storing user-specific data.
        """
        try:
            user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
            lang = context.user_data.get("lang") or self.google_sheets.get_user_state(user_id)

            print(f"Sending privacy policy to user {user_id} in language '{lang}'.")

            # Get the privacy policy link and localized prompt text.
            privacy_policy_link = self.utils.fetch_privacy_policy(lang, self.localization)
            accept_button = self.localization.get_string(lang, "privacy_accept")
            decline_button = self.localization.get_string(lang, "privacy_decline")
            prompt_text = self.localization.get_string(lang, "privacy_prompt")

            # Construct the message with the privacy policy link.
            message_text = f"{prompt_text}\n\n{privacy_policy_link}"

            # Inline buttons for consent options.
            keyboard = [
                [
                    InlineKeyboardButton(accept_button, callback_data="privacy_accept"),
                    InlineKeyboardButton(decline_button, callback_data="privacy_decline")
                ]
            ]

            # Send or edit the message based on how it was triggered.
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text=message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
                )
            else:
                await update.message.reply_text(
                    text=message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
                )

        except Exception as e:
            print(f"Error in send_privacy_policy handler: {e}")

    async def handle_privacy_response(self, update, context):
        """
        Handles user response to the privacy policy (accept/decline).
        Starts the application form if accepted.

        :param update: The update object containing callback query.
        :param context: The context object storing user-specific data.
        """
        query = update.callback_query  # Get callback query.
        await query.answer()  # Acknowledge the response.

        try:
            user_id = query.from_user.id

            # Retrieve user state to get language or use fallback.
            lang, current_question_index, responses = self.google_sheets.get_user_state(user_id)
            if not lang:
                lang = context.user_data.get("lang", "en")  # Fallback to default language if not found.
                print(f"Warning: No saved state found for user {user_id}, defaulting to language '{lang}'.")

            if query.data == "privacy_accept":
                print(f"User {user_id} accepted the privacy policy in language '{lang}'.")

                # Initialize a new application form.
                form = ApplicationForm(lang, self.localization)
                form.current_question_index = current_question_index  # Resume from saved question if exists.
                form.responses = responses  # Load previously saved responses.
                self.user_forms[user_id] = form

                # Save the initial state to Google Sheets.
                self.google_sheets.save_user_state(user_id, lang, form.current_question_index, form.responses)

                # Get the first question and send it to the user.
                question = form.get_next_question()
                start_message = self.localization.get_string(lang, "start_questionnaire")

                print(f"First question for user {user_id}: {question}")
                await query.edit_message_text(f"{start_message} {question}")

            elif query.data == "privacy_decline":
                print(f"User {user_id} declined the privacy policy.")
                decline_message = self.localization.get_string(lang, "decline_message")
                await query.edit_message_text(decline_message)

        except Exception as e:
            print(f"Error in handle_privacy_response handler: {e}")

    async def handle_response(self, update, context):
        """
        Processes user responses and progresses through the application form.
        Validates user input for email, phone number, and age questions.
        Saves user responses to Google Sheets when the form is complete.
        Handles cases where form state is restored from Google Sheets.
        """
        try:
            # Retrieve the user's Telegram ID from the update object.
            user_id = update.message.from_user.id

            # Attempt to get the user's active form from the in-memory storage.
            form = self.user_forms.get(user_id)

            # If the form is not found, try to restore the user's state from Google Sheets.
            if not form:
                lang, current_question_index, responses = self.google_sheets.get_user_state(user_id)
                if lang:
                    form = ApplicationForm(lang, self.localization)
                    form.current_question_index = current_question_index
                    form.responses = responses
                    self.user_forms[user_id] = form
                else:
                    await update.message.reply_text(self.localization.get_string("en", "error_message"))
                    return

            # Get the current question text and its type.
            user_response = update.message.text.strip()

            # Save the user's response to the current question.
            form.save_response(user_response)

            # Check if the form is complete (all questions answered).
            if form.is_complete():
                # Save the final state of the form to Metadata before removing it.
                self.google_sheets.save_user_state(user_id, form.lang, form.current_question_index, form.responses)

                # Map the responses and save them to the "Telegram Users" sheet.
                self.google_sheets.save_to_sheet(user_id, form.get_all_responses())

                # Notify the user of successful completion.
                await update.message.reply_text(self.localization.get_string(form.lang, "application_complete"))

                # Remove the form from memory.
                del self.user_forms[user_id]

                # Automatically approve the user's join request.
                await self.approve_join_request(user_id, context)
            else:
                # Get the next question to ask.
                next_question_text = form.get_next_question()

                # Save the current form state to Metadata.
                self.google_sheets.save_user_state(user_id, form.lang, form.current_question_index, form.responses)

                # Send the next question.
                await update.message.reply_text(next_question_text)

        except Exception as e:
            print(f"Error in handle_response handler: {e}")

    async def handle_join_request(self, update: Update, context):
        """
        Handles a new join request by initiating the onboarding process and saving the chat_id.
        """
        try:
            join_request = update.chat_join_request
            user_id = join_request.from_user.id
            chat_id = join_request.chat.id

            print(f"Received join request from user {user_id} for chat {chat_id}.")

            self.google_sheets.save_user_state(
                user_id=str(user_id),
                lang="",
                current_question_index=0,
                responses={},
                chat_id=str(chat_id)
            )
            await self.start(update, context)
        except Exception as e:
            print(f"Error in handle_join_request handler: {e}")

    async def approve_join_request(self, user_id, context):
        """
        Automatically approves the join request after the user completes the application.

        :param user_id: The Telegram user ID of the user.
        :param context: The context object storing user-specific data.
        """
        try:
            _, _, _, chat_id = self.google_sheets.get_user_state(user_id)
            if not chat_id:
                print(f"Error: Chat ID not found for user {user_id} in Metadata.")
                return

            print(f"Approving join request for user {user_id} in chat {chat_id}.")
            await context.bot.approve_chat_join_request(chat_id=int(chat_id), user_id=user_id)
            await self.utils.notify_admin(f"✅ User {user_id} has been approved to join the group.")
        except Exception as e:
            print(f"Error in approve_join_request handler: {e}")

    def setup(self, application):
        """
        Registers all handlers for commands and interactions.

        :param application: The Telegram application object.
        """
        print("Setting up command and message handlers.")
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_privacy_response, pattern="^privacy_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
