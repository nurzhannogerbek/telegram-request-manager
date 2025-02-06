import shared.telegram_bot.globals as globs
from telegram import Bot
from telegram.ext import Application
from shared.telegram_bot.logger import logger
from shared.telegram_bot.handlers import BotHandlers
from shared.telegram_bot.config import Config
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils

class Bootstrap:
    _google_sheets = GoogleSheets()
    _utils = Utils()

    @staticmethod
    def get_google_sheets():
        return Bootstrap._google_sheets

    @staticmethod
    def get_utils():
        return Bootstrap._utils

async def ensure_application_ready():
    if globs.application is None or globs.telegram_bot is None:
        logger.info("No global app/bot found, creating new Application.")
        globs.telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        globs.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        handlers = BotHandlers(Bootstrap.get_google_sheets(), Bootstrap.get_utils(), globs.telegram_bot)
        handlers.setup(globs.application)
    else:
        try:
            logger.info("Attempting 'getMe()' to ensure event loop is valid.")
            await globs.application.bot.get_me()
            logger.info("Loop is valid. Reusing global application & telegram_bot.")
        except Exception as e:
            logger.error(f"Error verifying application readiness: {e}", exc_info=True)
            raise
