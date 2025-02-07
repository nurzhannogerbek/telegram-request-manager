import shared.telegram_bot.globals as globs
from telegram import Bot
from telegram.ext import Application
from shared.telegram_bot.logger import logger
from shared.telegram_bot.handlers import BotHandlers
from shared.telegram_bot.config import Config
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils


class Bootstrap:
    """
    Bootstrap class to initialize and provide global instances for Google Sheets and utility classes.
    These instances are reused to optimize resource usage and performance in AWS Lambda hot starts.
    """
    _google_sheets = GoogleSheets()  # Cached instance of the Google Sheets client.
    _utils = Utils()  # Cached instance of utility functions.

    @staticmethod
    def get_google_sheets():
        """
        Provides the shared instance of the Google Sheets client.

        Returns:
            GoogleSheets: The shared instance of Google Sheets.
        """
        return Bootstrap._google_sheets

    @staticmethod
    def get_utils():
        """
        Provides the shared instance of utility functions.

        Returns:
            Utils: The shared instance of utility functions.
        """
        return Bootstrap._utils


async def ensure_application_ready():
    """
    Ensures that the Telegram bot application and its context are initialized and ready for handling updates.
    If no global application or bot exists, it creates and configures new instances.
    If the existing application is detected, its event loop is verified to be valid.

    Raises:
        Exception: If the event loop is not valid or if initialization fails.
    """
    if globs.application is None or globs.telegram_bot is None:
        # Create a new bot instance and application if no global instances exist.
        globs.telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        globs.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

        # Initialize and attach bot handlers to the application.
        handlers = BotHandlers(Bootstrap.get_google_sheets(), Bootstrap.get_utils(), globs.telegram_bot)
        handlers.setup(globs.application)
    else:
        try:
            # Verify that the event loop for the existing application is valid.
            await globs.application.bot.get_me()
        except Exception as e:
            # Log the error and re-raise it if verification fails.
            logger.error(f"Error verifying application readiness: {e}", exc_info=True)
            raise
