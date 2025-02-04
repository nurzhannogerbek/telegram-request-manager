from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.google_sheets import GoogleSheets
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
        Handles the language selection and stores the selected language in the user state.

        :param update: The Telegram update object containing the callback query.
        :param context: The context object to store user-specific data.
        """
        query = update.callback_query
        await query.answer()

        try:
            user_id = query.from_user.id
            lang = query.data.split("_")[1]  # Extract selected language code.

            print(f"User {user_id} selected language: {lang}.")
            context.user_data["lang"] = lang

            # Save the user's language selection to Google Sheets.
            self.google_sheets.save_user_state(user_id, lang)

            # Send the privacy policy in the selected language.
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
        Handles the user's response to the privacy policy (accept/decline).

        :param update: The Telegram update object containing the callback query.
        :param context: The context object storing user-specific data.
        """
        query = update.callback_query
        await query.answer()

        try:
            user_id = query.from_user.id
            lang = context.user_data.get("lang") or self.google_sheets.get_user_state(user_id)

            if query.data == "privacy_accept":
                print(f"User {user_id} accepted the privacy policy in language '{lang}'.")

                # Initialize the application form and store it.
                form = ApplicationForm(lang, self.localization)
                self.user_forms[user_id] = form

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

        :param update: The Telegram update object containing the user's response message.
        :param context: The context object storing user-specific data.
        """
        try:
            user_id = update.message.from_user.id
            form = self.user_forms.get(user_id)

            if not form:
                print(f"Warning: User {user_id} tried to respond without starting the form.")
                await update.message.reply_text(self.localization.get_string("en", "error_message"))
                return

            lang = form.lang
            print(f"User {user_id} responding in language '{lang}'.")

            # Save the user's response and check if the form is complete.
            form.save_response(update.message.text)

            if form.is_complete():
                print(f"User {user_id} completed the form. Saving responses to Google Sheets.")
                self.google_sheets.save_to_sheet(user_id, form.get_all_responses())
                await update.message.reply_text(self.localization.get_string(lang, "application_complete"))
                del self.user_forms[user_id]  # Clean up form data.
                await self.approve_join_request(user_id, context)
            else:
                next_question = form.get_next_question()
                print(f"Next question for user {user_id}: {next_question}")
                await update.message.reply_text(next_question)

        except Exception as e:
            print(f"Error in handle_response handler: {e}")

    async def handle_join_request(self, update: Update, context):
        """
        Handles a new join request by initiating the onboarding process.

        :param update: The Telegram update object containing the join request details.
        :param context: The context object storing user-specific data.
        """
        try:
            join_request = update.chat_join_request
            user_id = join_request.from_user.id
            print(f"Received join request from user {user_id}.")
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
            print(f"Approving join request for user {user_id}.")
            await context.bot.approve_chat_join_request(chat_id=context.chat_data["chat_id"], user_id=user_id)
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
