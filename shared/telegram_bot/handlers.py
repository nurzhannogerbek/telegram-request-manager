import logging
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
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
        Handles the /start command or a new join request by displaying language options.
        Sends a multilingual welcome message with inline buttons for language selection.
        """
        user_id = update.effective_user.id  # Extract the user ID from the update object.
        logger.info(f"User {user_id} triggered the language selection process.")  # Log the event.

        # Build the inline keyboard with language options.
        keyboard = [[
            InlineKeyboardButton("Русский", callback_data="lang_ru"),
            InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
            InlineKeyboardButton("English", callback_data="lang_en")
        ]]

        # Send the multilingual welcome message with the language selection buttons.
        await context.bot.send_message(
            chat_id=user_id,
            text=self.localization.get_multilang_welcome_message(),
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def set_language(self, update, context):
        """
        Sets the user's language based on their selection and sends the privacy policy request.
        """
        query = update.callback_query  # Extract the callback query object.
        await query.answer()  # Acknowledge the callback query.
        user_id = query.from_user.id  # Extract the user ID.
        lang = query.data.split("_")[1]  # Extract the selected language code.

        logger.info(f"User {user_id} selected language: {lang}.")  # Log the language selection.

        # Store the selected language for the user in the context.
        context.user_data["lang"] = lang

        # Proceed to send the privacy policy message.
        await self.send_privacy_policy_request(update, context)

    async def send_privacy_policy_request(self, update, context):
        """
        Sends a message requesting the user to review and accept the privacy policy.
        """
        user_id = update.effective_user.id  # Extract the user ID from the update object.
        lang = context.user_data.get("lang", "en")  # Default to English if language is not set.

        logger.info(f"Sending privacy policy request to user {user_id} in language {lang}.")  # Log the event.

        # Retrieve the privacy policy request message and button texts.
        policy_request_text = self.localization.get_string(lang, "privacy_policy_request")
        accept_button = self.localization.get_string(lang, "privacy_accept")
        decline_button = self.localization.get_string(lang, "privacy_decline")

        # Build the inline keyboard with "Agree" and "Disagree" buttons.
        keyboard = [[
            InlineKeyboardButton(accept_button, callback_data="privacy_accept"),
            InlineKeyboardButton(decline_button, callback_data="privacy_decline")
        ]]

        # Send the privacy policy request message.
        await context.bot.send_message(
            chat_id=user_id,
            text=policy_request_text,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def handle_privacy_response(self, update, context):
        """
        Handles the user's response to the privacy policy.
        """
        query = update.callback_query  # Extract the callback query object.
        await query.answer()  # Acknowledge the response.
        user_id = query.from_user.id  # Extract the user ID.
        lang = context.user_data.get("lang", "en")  # Default to English if not set.

        if query.data == "privacy_accept":
            logger.info(f"User {user_id} accepted the privacy policy.")  # Log acceptance.

            # Initialize a new application form for the user.
            self.user_forms[user_id] = ApplicationForm(lang, self.localization)
            question = self.user_forms[user_id].get_next_question()
            start_message = self.localization.get_string(lang, "start_questionnaire")

            # Send the first question of the form.
            await query.edit_message_text(f"{start_message} {question}")
        elif query.data == "privacy_decline":
            logger.info(f"User {user_id} declined the privacy policy.")  # Log decline.

            # Send a message indicating that the dialog is closed.
            decline_message = self.localization.get_string(lang, "decline_message")
            await query.edit_message_text(decline_message)

    async def handle_response(self, update, context):
        """
        Processes user responses and manages the application form flow.
        """
        user_id = update.message.from_user.id  # Extract the user ID.
        lang = context.user_data.get("lang", "en")  # Get the user's selected language.
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
            del self.user_forms[user_id]  # Clean up the form.

            # Approve the join request automatically.
            await self.approve_join_request(user_id, context)
        else:
            # Ask the next question in the form.
            next_question = form.get_next_question()
            logger.info(f"Asking the next question to user {user_id}.")  # Log the next question.
            await update.message.reply_text(next_question)

    async def handle_join_request(self, update: Update, context):
        """
        Handles new join requests and starts the onboarding process by displaying language options.
        """
        join_request = update.chat_join_request  # Extract the join request object.
        user_id = join_request.from_user.id  # Extract the user ID.

        logger.info(f"Received join request from user {user_id}.")  # Log the join request.

        # Trigger the language selection process.
        await self.start(update, context)

    async def approve_join_request(self, user_id, context):
        """
        Automatically approves the join request after the user completes the application.
        """
        logger.info(f"Approving join request for user {user_id}.")  # Log the approval action.

        # Approve the join request.
        await context.bot.approve_chat_join_request(chat_id=context.chat_data["chat_id"], user_id=user_id)
        await self.utils.notify_admin(f"✅ User {user_id} has been approved to join the group.")

    def setup(self, application):
        """
        Registers all command, message, and join request handlers with the application.
        """
        logger.info("Setting up command and message handlers.")  # Log the setup process.

        # Register handlers for bot commands and updates.
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_privacy_response, pattern="^privacy_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
