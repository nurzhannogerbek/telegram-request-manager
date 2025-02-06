import asyncio
import shared.telegram_bot.globals as globs
from telegram import Bot
from telegram.ext import Application
from shared.telegram_bot.logger import logger
from shared.telegram_bot.config import Config
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils
from shared.telegram_bot.handlers import BotHandlers

google_sheets = GoogleSheets()
utils = Utils()

def ensure_application_ready():
    logger.info("Checking if application and bot are ready.")
    if globs.application is None or globs.telegram_bot is None:
        logger.info("No global application or bot found, creating new instances.")
        globs.telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        globs.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        handlers = BotHandlers(google_sheets, utils, globs.telegram_bot)
        handlers.setup(globs.application)
        return
    try:
        logger.info("Attempting to check bot status using getMe().")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(globs.application.bot.get_me())
        logger.info("Existing application and bot are valid.")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("Event loop is closed. Re-creating application and bot.")
            globs.telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
            globs.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
            handlers = BotHandlers(google_sheets, utils, globs.telegram_bot)
            handlers.setup(globs.application)
        else:
            logger.error(f"Unexpected error while checking event loop: {e}", exc_info=True)
            raise
    except Exception as e:
        logger.error(f"Error during bot status check: {e}", exc_info=True)
