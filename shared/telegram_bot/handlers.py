from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils

class BotHandlers:
    """
    Class to handle bot commands, messages, and user interactions for the application form.
    """

    def __init__(self):
        """
        Initializes the bot handlers with necessary components including localization,
        Google Sheets integration, and user-specific application forms.
        """
        self.user_forms = {}  # Dictionary to store active application forms keyed by user ID.
        self.localization = Localization()  # Handles localized strings and questions.
        self.google_sheets = GoogleSheets()  # Manages Google Sheets data storage.
        self.utils = Utils()  # Utility functions, including notifications.

    async def start(self, update, context):
        """
        Handles the /start command to begin language selection.
        Sends a welcome message with language options.

        :param update: The update object containing information about the incoming message.
        :param context: The context object to manage user-specific data.
        """
        try:
            user_id = update.effective_user.id  # Get the user ID initiating the command.
            print(f"User {user_id} issued the /start command.")

            # Language selection buttons.
            keyboard = [[
                InlineKeyboardButton("Русский", callback_data="lang_ru"),
                InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
                InlineKeyboardButton("English", callback_data="lang_en")
            ]]

            # Send welcome message with language selection options.
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
        Sends the privacy policy in the selected language.

        :param update: The update object containing the callback query.
        :param context: The context object to store user-specific data.
        """
        query = update.callback_query  # Get callback query.
        await query.answer()  # Acknowledge the query.

        try:
            user_id = query.from_user.id  # Get user ID.
            lang = query.data.split("_")[1]  # Extract the selected language code.

            print(f"User {user_id} selected language: {lang}.")
            context.user_data["lang"] = lang  # Store language in context.

            # Send the privacy policy using the chosen language.
            await self.send_privacy_policy(update, context)
        except Exception as e:
            print(f"Error in set_language handler: {e}")

    async def send_privacy_policy(self, update, context):
        """
        Sends the privacy policy link in the user's selected language and prompts for consent.

        :param update: The update object containing callback query or message.
        :param context: The context object storing user-specific data.
        """
        try:
            user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
            lang = context.user_data.get("lang", "en")  # Get user's selected language.

            print(f"Sending privacy policy to user {user_id} in language '{lang}'.")

            # Get the URL of the privacy policy and localized text.
            privacy_policy_link = self.utils.fetch_privacy_policy(lang, self.localization)
            accept_button = self.localization.get_string(lang, "privacy_accept")
            decline_button = self.localization.get_string(lang, "privacy_decline")
            prompt_text = self.localization.get_string(lang, "privacy_prompt")

            # Construct the message combining the privacy policy link.
            message_text = f"{prompt_text}\n\n{privacy_policy_link}"

            # Inline buttons for consent.
            keyboard = [
                [
                    InlineKeyboardButton(accept_button, callback_data="privacy_accept"),
                    InlineKeyboardButton(decline_button, callback_data="privacy_decline")
                ]
            ]

            # Send or edit the message based on how it was triggered.
            if update.callback_query:
                await update.callback_query.edit_message_text(
                    text=message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")
            else:
                await update.message.reply_text(
                    text=message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown")

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
            lang = context.user_data.get("lang", "en")  # Retrieve selected language.

            if query.data == "privacy_accept":
                print(f"User {user_id} accepted the privacy policy in language '{lang}'.")

                # Initialize the application form and store it.
                form = ApplicationForm(lang, self.localization)
                self.user_forms[user_id] = form

                # Get the first question.
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

        :param update: The update object containing user messages.
        :param context: The context object storing user-specific data.
        """
        try:
            user_id = update.message.from_user.id  # Get user ID.
            form = self.user_forms.get(user_id)  # Retrieve the user's form.

            if not form:
                print(f"Warning: User {user_id} tried to respond without starting the form.")
                await update.message.reply_text(self.localization.get_string("en", "error_message"))
                return

            # Use language stored in the form.
            lang = form.lang
            print(f"User {user_id} responding in language '{lang}'.")

            # Save the response and check form completion.
            form.save_response(update.message.text)

            if form.is_complete():
                print(f"User {user_id} completed the form. Saving responses.")
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
        Handles join requests and triggers the start of the onboarding process.

        :param update: The update object containing join request details.
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
        Automatically approves the join request once the user completes the form.

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
