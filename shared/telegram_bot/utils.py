from shared.telegram_bot.logger import logger
from shared.telegram_bot.config import Config
from shared.telegram_bot.globals import telegram_bot

class Utils:
    def __init__(self):
        logger.info("Utils.__init__ called.")
        self.bot = telegram_bot
        self.admin_chat_id = Config.ADMIN_CHAT_ID
        logger.info(f"Utils initialized. admin_chat_id={self.admin_chat_id}")

    def notify_admin(self, message):
        logger.info(f"notify_admin called with message={message}")
        try:
            self.bot.send_message(chat_id=self.admin_chat_id, text=message)
            logger.info("notify_admin: Message sent successfully.")
        except Exception as e:
            logger.error(f"Error sending notification to admin: {e}", exc_info=True)

    def notify_admin_group(self, message, admin_group_chat_id):
        logger.info(f"notify_admin_group called with admin_group_chat_id={admin_group_chat_id}, message={message}")
        try:
            self.bot.send_message(chat_id=admin_group_chat_id, text=message)
            logger.info("notify_admin_group: Message sent successfully.")
        except Exception as e:
            logger.error(f"Error sending notification to admin group: {e}", exc_info=True)

    def send_user_message(self, user_id, message):
        logger.info(f"send_user_message called for user_id={user_id}, message={message}")
        try:
            self.bot.send_message(chat_id=user_id, text=message)
            logger.info(f"send_user_message: Message sent to user {user_id}.")
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {e}", exc_info=True)

    def send_error_notification(self, error_message):
        logger.info(f"send_error_notification called with error_message={error_message}")
        try:
            self.notify_admin(f"❌ Error occurred: {error_message}")
        except Exception as e:
            logger.error(f"Error sending error notification to admin: {e}", exc_info=True)

    @staticmethod
    def fetch_privacy_policy(lang, localization):
        logger.info(f"fetch_privacy_policy called for lang={lang}")
        policy_url = Config.get_privacy_policy_url(lang)
        if not policy_url:
            logger.info("No policy URL found, returning localized error message.")
            return localization.get_string(lang, "error_message")

        link_text = localization.get_string(lang, "privacy_policy_link_text")
        logger.info(f"Returning privacy policy URL for lang={lang}")
        return f"🔗[{link_text}]({policy_url})"
