from shared.telegram_bot.globals import telegram_bot, google_sheets, utils

class Bootstrap:
    @staticmethod
    def get_telegram_bot():
        return telegram_bot

    @staticmethod
    def get_google_sheets():
        return google_sheets

    @staticmethod
    def get_utils():
        return utils
