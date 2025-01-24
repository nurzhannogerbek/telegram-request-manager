from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils

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

    @staticmethod
    async def start(update, context):
        """
        Handles the /start command to initialize language selection.

        Sends a message with inline buttons for the user to choose their preferred language.
        """
        user_id = update.message.from_user.id  # Extracts user ID from the update object.
        keyboard = [[
            InlineKeyboardButton("Русский", callback_data="lang_ru"),
            InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
            InlineKeyboardButton("English", callback_data="lang_en")
        ]]
        # Sends a message with language selection buttons.
        await update.message.reply_text(
            "Please choose your language:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def set_language(self, update, context):
        """
        Sets the user's language and starts the application form.

        :param update: Telegram update object containing the callback query.
        :param context: Telegram context object for managing the bot state.
        """
        query = update.callback_query  # Extracts the callback query object.
        await query.answer()  # Acknowledges the callback query.
        user_id = query.from_user.id  # Extracts the user ID.
        lang = query.data.split("_")[1]  # Extracts the selected language code.

        # Initializes a new application form for the user in the chosen language.
        self.user_forms[user_id] = ApplicationForm(lang, self.localization)
        question = self.user_forms[user_id].get_next_question()  # Gets the first question.

        # Sends the first question to the user.
        await query.edit_message_text(f"Welcome! Please answer the following question:\n{question}")

    async def handle_response(self, update, context):
        """
        Processes user responses and manages the application form flow.

        :param update: Telegram update object containing the user's message.
        :param context: Telegram context object for managing the bot state.
        """
        user_id = update.message.from_user.id  # Extracts user ID from the update object.
        form = self.user_forms.get(user_id)  # Retrieves the user's form, if it exists.

        if not form:
            # If no form exists, prompts the user to start with the /start command.
            await update.message.reply_text("Please start with /start.")
            return

        # Saves the user's response to the current question.
        form.save_response(update.message.text)

        if form.is_complete():
            # If the form is complete, save the responses to Google Sheets.
            self.google_sheets.save_to_sheet(user_id, form.responses)
            await update.message.reply_text("Thank you! Your application has been submitted.")
            del self.user_forms[user_id]  # Deletes the form to free up memory.
        else:
            # If the form is not complete, ask the next question.
            next_question = form.get_next_question()
            await update.message.reply_text(next_question)

    async def handle_join_request(self, update: Update, context):
        """
        Handles new join requests to the group and decides to approve or decline them.

        :param update: Telegram update object containing the join request.
        :param context: Telegram context object for managing the bot state.
        """
        join_request = update.chat_join_request  # Extracts the join request object.
        user_id = join_request.from_user.id  # Extracts the user ID of the requester.
        chat_id = join_request.chat.id  # Extracts the chat ID of the group.

        if user_id in self.user_forms and self.user_forms[user_id].is_complete():
            # If the form is complete, approve the join request.
            await context.bot.approve_chat_join_request(chat_id=chat_id, user_id=user_id)
            # Notify the admin about the approval.
            await self.utils.notify_admin(
                f"✅ User {join_request.from_user.full_name} has been approved to join the group."
            )
        else:
            # If the form is incomplete, decline the join request.
            await context.bot.decline_chat_join_request(chat_id=chat_id, user_id=user_id)
            # Notify the admin about the decline.
            await self.utils.notify_admin(
                f"❌ User {join_request.from_user.full_name} has been declined due to incomplete data."
            )

    def setup(self, application):
        """
        Registers all command, message, and join request handlers with the application.

        :param application: Telegram application instance.
        """
        # Registers the /start command handler.
        application.add_handler(CommandHandler("start", self.start))
        # Registers the callback query handler for language selection.
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        # Registers the message handler for user responses.
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        # Registers the handler for new join requests.
        application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
