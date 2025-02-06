from shared.telegram_bot.main import TelegramBot
from shared.telegram_bot.utils import Utils
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.config import Config

class Bootstrap:
    telegram_bot = TelegramBot(Config.TELEGRAM_BOT_TOKEN)
    utils = Utils()
    google_sheets = GoogleSheets()

    @staticmethod
    def get_telegram_bot():
        return Bootstrap.telegram_bot

    @staticmethod
    def get_utils():
        return Bootstrap.utils

    @staticmethod
    def get_google_sheets():
        return Bootstrap.google_sheets
