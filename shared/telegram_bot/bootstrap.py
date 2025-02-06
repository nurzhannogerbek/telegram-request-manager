import asyncio
from telegram import Bot
from telegram.ext import Application
from shared.telegram_bot.logger import logger
from shared.telegram_bot.handlers import BotHandlers
from shared.telegram_bot.config import Config
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils
import shared.telegram_bot.globals as globs

google_sheets = GoogleSheets()
utils = Utils()

def ensure_application_ready():
    if globs.application is None or globs.telegram_bot is None:
        logger.info("No global app/bot found, creating new Application.")
        globs.telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        globs.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        handlers = BotHandlers()
        handlers.setup(globs.application)
        return

    try:
        logger.info("Attempting 'getMe()' to ensure event loop is valid.")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(globs.application.bot.get_me())
        logger.info("Loop is valid. Reusing global application & telegram_bot.")
    except RuntimeError as e:
        if "Event loop is closed" in str(e):
            logger.warning("Detected a closed event loop. Re-creating app/bot.")
            globs.telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
            globs.application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
            handlers = BotHandlers()
            handlers.setup(globs.application)
        else:
            raise
    except Exception as e:
        logger.error(f"Error calling getMe(), not a loop-close: {e}", exc_info=True)

def get_google_sheets():
    return google_sheets

def get_utils():
    return utils
