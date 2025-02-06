from telegram.ext import Application
from telegram import Bot
from shared.telegram_bot.config import Config

telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
