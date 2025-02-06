from telegram.ext import Application
from telegram import Bot
from shared.telegram_bot.config import Config
from shared.telegram_bot.logger import logger

logger.info("Initializing telegram_bot and application in globals.py")

telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
