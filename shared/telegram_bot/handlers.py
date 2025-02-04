import logging
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters, ContextTypes
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils

# Configure logging to track bot activities and errors.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BotHandlers:
    """
    Class to manage all bot command and message handlers.
    """

    def __init__(self):
        """
        Initializes required components for handling user interactions, localization,
        Google Sheets integration, and utility functions.
        """
        self.user_forms = {}  # Stores active user forms keyed by user ID.
        self.localization = Localization()  # Handles localization for user interactions.
        self.google_sheets = GoogleSheets()  # Manages Google Sheets for storing user data.
        self.utils = Utils()  # Provides utility functions like admin notifications.

    async def start(self, update, context):
        """
        Handles the /start command to initialize language selection.
        Sends a message with inline buttons for the user to choose their preferred language.

        :param update: Telegram update containing the /start command.
        :param context: Context object providing bot and update data.
        """
        user_id = update.message.from_user.id  # Extract the user ID from the update object.
        logger.info(f"User {user_id} issued the /start command.")  # Log the start command.

        # Display language options as inline buttons.
        keyboard = [[
            InlineKeyboardButton("Русский", callback_data="lang_ru"),
            InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
            InlineKeyboardButton("English", callback_data="lang_en")
        ]]

        # Send the message prompting the user to select a language.
        await update.message.reply_text(
            self.localization.get_string("en", "choose_language"),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def set_language(self, update, context):
        """
        Sets the user's language based on their selection and sends the privacy policy.

        :param update: Telegram update containing the user's language selection.
        :param context: Context object to store user-specific data.
        """
        query = update.callback_query  # Extract the callback query object.
        await query.answer()  # Acknowledge the callback query to avoid delays.
        user_id = query.from_user.id  # Extract the user ID.
        lang = query.data.split("_")[1]  # Extract the selected language code from callback data.

        logger.info(f"User {user_id} selected language: {lang}.")  # Log the selected language.

        # Store the selected language in the context.
        context.user_data["lang"] = lang

        # Proceed to send the privacy policy.
        await self.send_privacy_policy(update, context)

    async def send_privacy_policy(self, update, context):
        """
        Sends the privacy policy to the user and asks for their consent.

        :param update: Telegram update object.
        :param context: Context object storing user-specific data.
        """
        user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
        lang = context.user_data.get("lang", "en")  # Default to English if no language is set.

        logger.info(f"Sending privacy policy to user {user_id} in language {lang}.")  # Log the action.

        # Retrieve the privacy policy and button texts based on the selected language.
        privacy_policy_text = self.utils.fetch_privacy_policy(lang)
        accept_button = self.localization.get_string(lang, "privacy_accept")
        decline_button = self.localization.get_string(lang, "privacy_decline")
        prompt_text = self.localization.get_string(lang, "privacy_prompt")

        # Build the inline keyboard for the user's response.
        keyboard = [[
            InlineKeyboardButton(accept_button, callback_data="privacy_accept"),
            InlineKeyboardButton(decline_button, callback_data="privacy_decline")
        ]]

        # Send the privacy policy with response buttons.
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=f"{prompt_text}\n\n{privacy_policy_text}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await update.message.reply_text(
                text=f"{prompt_text}\n\n{privacy_policy_text}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    async def handle_privacy_response(self, update, context):
        """
        Handles the user's response to the privacy policy.

        :param update: Telegram update containing the user's response.
        :param context: Context object storing user-specific data.
        """
        query = update.callback_query  # Extract the callback query object.
        await query.answer()  # Acknowledge the user's response.
        user_id = query.from_user.id  # Extract the user ID.
        lang = context.user_data.get("lang", "en")  # Default to English if no language is set.

        if query.data == "privacy_accept":
            logger.info(f"User {user_id} accepted the privacy policy.")  # Log the user's acceptance.

            # Initialize a new application form for the user.
            self.user_forms[user_id] = ApplicationForm(lang, self.localization)
            question = self.user_forms[user_id].get_next_question()
            start_message = self.localization.get_string(lang, "start_questionnaire")

            # Send the first question to the user.
            await query.edit_message_text(f"{start_message} {question}")
        elif query.data == "privacy_decline":
            logger.info(f"User {user_id} declined the privacy policy.")  # Log the user's rejection.

            # Send a message indicating that the conversation has ended.
            decline_message = self.localization.get_string(lang, "decline_message")
            await query.edit_message_text(decline_message)

    async def handle_response(self, update, context):
        """
        Processes the user's responses to the questions in the application form.

        :param update: Telegram update containing the user's response.
        :param context: Context object providing user-specific data.
        """
        user_id = update.message.from_user.id  # Extract the user ID.
        lang = context.user_data.get("lang", "en")  # Retrieve the user's selected language.
        form = self.user_forms.get(user_id)  # Retrieve the active form for the user.

        if not form:
            logger.warning(f"User {user_id} tried to respond without starting the form.")  # Log the warning.
            await update.message.reply_text(self.localization.get_string(lang, "error_message"))
            return

        logger.info(f"Saving response from user {user_id}: {update.message.text}.")  # Log the response.

        # Save the user's response to the current question.
        form.save_response(update.message.text)

        if form.is_complete():
            logger.info(f"User {user_id} completed the form. Saving responses to Google Sheets.")  # Log completion.

            # Save responses to Google Sheets.
            self.google_sheets.save_to_sheet(user_id, form.responses)
            complete_message = self.localization.get_string(lang, "application_complete")

            # Notify the user of successful form submission.
            await update.message.reply_text(complete_message)
            del self.user_forms[user_id]  # Clean up the form data.

            # Approve the user's join request automatically.
            await self.approve_join_request(user_id, context)
        else:
            # Ask the next question in the form.
            next_question = form.get_next_question()
            logger.info(f"Asking the next question to user {user_id}.")  # Log the action.
            await update.message.reply_text(next_question)

    async def handle_join_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """
        Handles new join requests and starts the onboarding process by sending a welcome message.

        :param update: Telegram update containing the join request.
        :param context: Context object for managing bot interactions.
        """
        join_request = update.chat_join_request  # Extract the join request object.
        user_id = join_request.from_user.id  # Extract the user ID of the joining user.
        lang = "en"  # Default language is English.

        logger.info(f"Received join request from user {user_id}.")  # Log the received request.

        # Send a welcome message and prompt for language selection.
        welcome_message = self.localization.get_string(lang, "welcome_message")
        language_prompt = self.localization.get_string(lang, "choose_language")

        # Display language options as inline buttons.
        keyboard = [[
            InlineKeyboardButton("Русский", callback_data="lang_ru"),
            InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
            InlineKeyboardButton("English", callback_data="lang_en")
        ]]

        # Send the welcome message along with language selection options.
        await context.bot.send_message(
            chat_id=user_id,
            text=f"{welcome_message}\n\n{language_prompt}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def approve_join_request(self, user_id, context):
        """
        Automatically approves the user's join request after completing the application form.

        :param user_id: Telegram user ID of the user to be approved.
        :param context: Context object for managing bot interactions.
        """
        logger.info(f"Approving join request for user {user_id}.")  # Log the approval action.

        # Approve the user's join request.
        await context.bot.approve_chat_join_request(chat_id=context.chat_data["chat_id"], user_id=user_id)
        await self.utils.notify_admin(f"✅ User {user_id} has been approved to join the group.")

    def setup(self, application):
        """
        Registers all command, message, and join request handlers with the application.

        :param application: Telegram Application instance.
        """
        logger.info("Setting up command and message handlers.")  # Log the setup process.

        # Register handlers for commands, messages, and join requests.
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_privacy_response, pattern="^privacy_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
