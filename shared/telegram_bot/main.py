from telegram.ext import ApplicationBuilder
from shared.telegram_bot.handlers import BotHandlers


class TelegramBot:
    """
    Main class to manage the Telegram bot using the latest API, either through polling or webhook updates.
    """

    def __init__(self, token):
        """
        Initializes the Telegram bot with the given token and sets up handlers.

        :param token: Telegram bot token as a string.
        """
        self.token = token  # Store the bot token securely.

        # Initialize the application using ApplicationBuilder, which configures the bot.
        self.application = ApplicationBuilder().token(token).build()

        # Initialize and set up bot handlers for commands, messages, and events.
        self.handlers = BotHandlers()
        self.handlers.setup(self.application)  # Register all the required handlers.

    def run_polling(self):
        """
        Starts the Telegram bot using long polling.
        This is generally used in development or non-production setups.
        """
        # Run the bot using long polling to fetch updates from the Telegram server.
        self.application.run_polling()

    def process_update(self, update):
        """
        Processes a single Telegram update.
        This method is typically used when the bot is running via webhook.

        :param update: A Telegram Update object containing user interactions.
        """
        # Use the built-in method to process updates received through webhooks.
        self.application.process_update(update)
