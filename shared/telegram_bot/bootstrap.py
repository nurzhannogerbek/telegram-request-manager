import shared.telegram_bot.globals as globs
from telegram import Bot
from telegram.ext import Application
from shared.telegram_bot.handlers import BotHandlers
from shared.telegram_bot.config import Config
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils
from telegram.ext import ContextTypes
from telegram.error import Forbidden, BadRequest, TimedOut, NetworkError
from shared.telegram_bot.logger import logger
from telegram import Update


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


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """
    Global error handler to catch and log known exceptions during update processing.
    """
    error = context.error
    if isinstance(error, Forbidden):
        logger.warning(f"❌ Forbidden: Cannot message user. Details: {error}")
    elif isinstance(error, BadRequest):
        logger.warning(f"⚠️ BadRequest: Likely caused by bad parameters. Details: {error}")
    elif isinstance(error, TimedOut):
        logger.warning(f"⏱️ TimedOut: The bot took too long to respond. Details: {error}")
    elif isinstance(error, NetworkError):
        logger.warning(f"🌐 NetworkError: Connection issue. Details: {error}")
    else:
        logger.error("🔥 Unhandled exception occurred", exc_info=True)
        if update:
            logger.debug(f"Update that caused the error: {update}")


async def ensure_application_ready():
    """
    Ensures that the Telegram bot application and its context are properly initialized.
    This function is intended to be idempotent and safe to call multiple times.

    - If the application and bot instances are not initialized, it creates and configures them.
    - Registers all required handlers for processing updates.
    - Registers a global error handler to capture any unhandled exceptions during update processing.
    - If already initialized, performs a health check to ensure the bot is responsive.

    Raises:
        Exception: If bot initialization or health check fails.
    """
    if globs.application is None or globs.telegram_bot is None:
        # Create the Telegram Bot instance using the token from configuration.
        globs.telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)

        # Build the Application instance that will manage updates and handlers.
        globs.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()

        # Initialize and register all handlers (commands, messages, callbacks, etc.).
        handlers = BotHandlers(
            google_sheets=GoogleSheets(),
            utils=Utils(),
            bot=globs.telegram_bot
        )
        handlers.setup(globs.application)

        # Register the global error handler to catch and log unexpected errors.
        globs.application.add_error_handler(error_handler)
    else:
        try:
            # Explicitly initialize the application before accessing .bot
            await globs.application.initialize()

            # Perform health check to ensure bot token is valid and responsive
            await globs.application.bot.get_me() # type: ignore[attr-defined]

        except Exception as e:
            logger.error(f"Failed to verify Telegram bot availability: {e}", exc_info=True)
            raise


async def post_init_and_process(update_data: dict):
    """
    Initializes the Telegram bot application if needed and processes a single Telegram update.

    This function is designed to be used in a "fire-and-forget" fashion inside AWS Lambda
    to minimize cold start latency by allowing the response to return immediately after
    launching this task asynchronously.

    Args:
        update_data (dict): The raw update payload received from the Telegram webhook.
    """
    try:
        # Convert raw update data into a Telegram Update object.
        update = Update.de_json(update_data, globs.application.bot)

        # Process the update using the Application instance.
        await globs.application.process_update(update)
    except Exception as e:
        # Log any errors that occur during processing (do not raise).
        logger.error(f"❌ Error while processing update in post_init_and_process: {e}", exc_info=True)