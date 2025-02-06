from shared.telegram_bot.logger import logger
from shared.telegram_bot.bootstrap import Bootstrap


class Utils:
    def __init__(self):
        self.bot = Bootstrap.get_telegram_bot().application.bot
        self.admin_chat_id = Bootstrap.get_utils().admin_chat_id

    def notify_admin(self, message):
        try:
            self.bot.send_message(chat_id=self.admin_chat_id, text=message)
        except Exception as e:
            logger.error(f"Error sending notification to admin: {e}", exc_info=True)

    def notify_admin_group(self, message, admin_group_chat_id):
        try:
            self.bot.send_message(chat_id=admin_group_chat_id, text=message)
        except Exception as e:
            logger.error(f"Error sending notification to admin group: {e}", exc_info=True)

    def send_user_message(self, user_id, message):
        try:
            self.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {e}", exc_info=True)

    def send_error_notification(self, error_message):
        try:
            self.notify_admin(f"❌ Error occurred: {error_message}")
        except Exception as e:
            logger.error(f"Error sending error notification to admin: {e}", exc_info=True)

    @staticmethod
    def fetch_privacy_policy(lang, localization):
        policy_url = Bootstrap.get_utils().fetch_privacy_policy_url(lang)
        if not policy_url:
            return localization.get_string(lang, "error_message")

        link_text = localization.get_string(lang, "privacy_policy_link_text")
        return f"🔗[{link_text}]({policy_url})"
