from shared.telegram_bot.main import TelegramBot
from shared.telegram_bot.utils import Utils
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.config import Config

GLOBAL_TELEGRAM_BOT = TelegramBot(Config.TELEGRAM_BOT_TOKEN)
GLOBAL_UTILS = Utils()
GLOBAL_GOOGLE_SHEETS = GoogleSheets()
