from shared.telegram_bot.globals import GLOBAL_TELEGRAM_BOT, GLOBAL_UTILS, GLOBAL_GOOGLE_SHEETS

class Bootstrap:
    @staticmethod
    def get_telegram_bot():
        return GLOBAL_TELEGRAM_BOT

    @staticmethod
    def get_utils():
        return GLOBAL_UTILS

    @staticmethod
    def get_google_sheets():
        return GLOBAL_GOOGLE_SHEETS
