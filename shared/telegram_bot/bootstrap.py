from shared.telegram_bot.globals import telegram_bot, application
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.logger import logger
from shared.telegram_bot.utils import Utils

class Bootstrap:
    logger.info("Creating global GoogleSheets and Utils instances in Bootstrap.")
    google_sheets = GoogleSheets()
    utils = Utils()

    @staticmethod
    def get_telegram_bot():
        logger.info("Bootstrap.get_telegram_bot called.")
        return telegram_bot

    @staticmethod
    def get_application():
        logger.info("Bootstrap.get_application called.")
        return application

    @staticmethod
    def get_google_sheets():
        logger.info("Bootstrap.get_google_sheets called.")
        return Bootstrap.google_sheets

    @staticmethod
    def get_utils():
        logger.info("Bootstrap.get_utils called.")
        return Bootstrap.utils
