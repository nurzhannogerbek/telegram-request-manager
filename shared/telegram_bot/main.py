from telegram.ext import Application
from shared.telegram_bot.handlers import BotHandlers
from telegram import Update


class TelegramBot:
    """
    Main class to manage the Telegram bot using the latest API.
    """

    def __init__(self, token):
        """
        Initializes the Telegram bot with the given token.

        :param token: Telegram bot token as a string.
        """
        self.token = token  # Store the bot token.
        # Initialize the application.
        self.application = Application.builder().token(token).build()
        self.handlers = BotHandlers()  # Initialize bot handlers.

        # Register all handlers.
        self.handlers.setup(self.application)

    async def process_update(self, update_data):
        """
        Process a single Telegram update using the bot's application.

        :param update_data: Dictionary containing the Telegram update.
        """
        # Parse the update and process it through handlers.
        update = Update.de_json(update_data, self.application.bot)
        await self.application.process_update(update)
