from telegram.ext import ApplicationBuilder
from shared.telegram_bot.handlers import BotHandlers

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
        # Create the application using the new ApplicationBuilder.
        self.application = ApplicationBuilder().token(token).build()
        self.handlers = BotHandlers()  # Initialize handlers.

    def run(self):
        """
        Starts the Telegram bot, sets up handlers, and begins polling.
        """
        # Set up handlers in the application.
        self.handlers.setup(self.application)

        # Run the application using polling.
        self.application.run_polling()
