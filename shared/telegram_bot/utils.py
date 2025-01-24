import os
import requests
from telegram import Bot

class Utils:
    """
    Utility class for managing common bot-related functions such as notifications and fetching external resources.
    """

    def __init__(self):
        """
        Initializes the utility class by loading environment variables for bot token and admin chat ID.
        """
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Telegram bot token
        if not self.bot_token:
            raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")

        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")  # Admin chat ID
        if not self.admin_chat_id:
            raise EnvironmentError("ADMIN_CHAT_ID environment variable is not set.")

        self.bot = Bot(token=self.bot_token)  # Initialize the Telegram bot instance

    def notify_admin(self, message):
        """
        Sends a notification message to the administrator's Telegram chat.

        :param message: The message to send to the administrator.
        """
        try:
            self.bot.send_message(chat_id=self.admin_chat_id, text=message)
        except Exception as e:
            print(f"Error sending notification to admin: {e}")

    def notify_admin_group(self, message, admin_group_chat_id):
        """
        Sends a notification message to the admin group chat.

        :param message: The message to send to the admin group chat.
        :param admin_group_chat_id: The Telegram chat ID of the admin group.
        """
        try:
            self.bot.send_message(chat_id=admin_group_chat_id, text=message)
        except Exception as e:
            print(f"Error sending notification to admin group: {e}")

    def send_user_message(self, user_id, message):
        """
        Sends a message to a specific user.

        :param user_id: The Telegram user ID of the recipient.
        :param message: The message to send to the user.
        """
        try:
            self.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Error sending message to user {user_id}: {e}")

    def send_error_notification(self, error_message):
        """
        Sends an error notification to the administrator.

        :param error_message: The error message to notify the admin about.
        """
        try:
            self.notify_admin(f"❌ Error occurred: {error_message}")
        except Exception as e:
            print(f"Error sending error notification to admin: {e}")

    @staticmethod
    def fetch_privacy_policy(lang):
        """
        Fetches the privacy policy text for the specified language from an external source.

        :param lang: Language code (e.g., 'ru', 'kz', 'en').
        :return: Text of the privacy policy or a fallback message if unavailable.
        """
        policy_urls = {
            "ru": os.getenv("PRIVACY_POLICY_URL_RU"),
            "kz": os.getenv("PRIVACY_POLICY_URL_KZ"),
            "en": os.getenv("PRIVACY_POLICY_URL_EN"),
        }

        url = policy_urls.get(lang, policy_urls["ru"])  # Default to English if language not found.
        if not url:
            return "Privacy policy URL is not configured for this language."

        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching privacy policy for language '{lang}': {e}")
            return "Privacy policy is currently unavailable. Please try again later."
