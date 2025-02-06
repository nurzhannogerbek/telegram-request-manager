from shared.telegram_bot.main import TelegramBot
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils
from shared.telegram_bot.config import Config

telegram_bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN)
google_sheets = GoogleSheets()
utils = Utils()
