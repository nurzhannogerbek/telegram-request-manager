from shared.telegram_bot.globals import telegram_bot, application
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils

class Bootstrap:
    google_sheets = GoogleSheets()
    utils = Utils()

    @staticmethod
    def get_telegram_bot():
        return telegram_bot

    @staticmethod
    def get_application():
        return application

    @staticmethod
    def get_google_sheets():
        return Bootstrap.google_sheets

    @staticmethod
    def get_utils():
        return Bootstrap.utils
