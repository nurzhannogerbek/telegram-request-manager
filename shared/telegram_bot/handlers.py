from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
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
        Initializes required components for handling user interactions.
        """
        self.user_forms = {}
        self.localization = Localization()
        self.google_sheets = GoogleSheets()
        self.utils = Utils()

    @staticmethod
    async def start(update, context):
        """
        Handles the /start command to initialize language selection.

        Sends a message with inline buttons for the user to choose their preferred language.
        """
        user_id = update.message.from_user.id
        keyboard = [[
            InlineKeyboardButton("Русский", callback_data="lang_ru"),
            InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
            InlineKeyboardButton("English", callback_data="lang_en")
        ]]
        await update.message.reply_text(
            "Please choose your language:", reply_markup=InlineKeyboardMarkup(keyboard)
        )

    async def set_language(self, update, context):
        """
        Sets the user's language and starts the application form.
        """
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        lang = query.data.split("_")[1]

        self.user_forms[user_id] = ApplicationForm(lang, self.localization)
        question = self.user_forms[user_id].get_next_question()
        await query.edit_message_text(f"Welcome! Please answer the following question:\n{question}")

    async def handle_response(self, update, context):
        """
        Processes user responses and manages application form flow.
        """
        user_id = update.message.from_user.id
        form = self.user_forms.get(user_id)

        if not form:
            await update.message.reply_text("Please start with /start.")
            return

        form.save_response(update.message.text)

        if form.is_complete():
            self.google_sheets.save_to_sheet(user_id, form.responses)
            await update.message.reply_text("Thank you! Your application has been submitted.")
            del self.user_forms[user_id]
        else:
            next_question = form.get_next_question()
            await update.message.reply_text(next_question)

    def setup(self, application):
        """
        Registers all command and message handlers with the application.

        :param application: Telegram application instance.
        """
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
