from telegram import Bot
from telegram.ext import Application
from shared.telegram_bot.config import Config
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils

telegram_bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
google_sheets = GoogleSheets()
utils = Utils()
