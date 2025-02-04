import os
from telegram import Bot

class Utils:
    """
    Utility class for managing common bot-related functions such as notifications and fetching external resources.
    """

    def __init__(self):
        """
        Initializes the utility class by loading environment variables for the bot token and admin chat ID.
        """
        # Load the Telegram bot token from environment variables.
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            # Raise an error if the token is missing.
            raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")

        # Load the admin chat ID from environment variables.
        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        if not self.admin_chat_id:
            # Raise an error if the chat ID is missing.
            raise EnvironmentError("ADMIN_CHAT_ID environment variable is not set.")

        # Initialize the Telegram bot using the provided token.
        self.bot = Bot(token=self.bot_token)

    def notify_admin(self, message):
        """
        Sends a notification message to the administrator's Telegram chat.
        """
        try:
            self.bot.send_message(chat_id=self.admin_chat_id, text=message)
        except Exception as e:
            print(f"Error sending notification to admin: {e}")

    def notify_admin_group(self, message, admin_group_chat_id):
        """
        Sends a notification message to the admin group chat.
        """
        try:
            self.bot.send_message(chat_id=admin_group_chat_id, text=message)
        except Exception as e:
            print(f"Error sending notification to admin group: {e}")

    def send_user_message(self, user_id, message):
        """
        Sends a message to a specific user.
        """
        try:
            self.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            print(f"Error sending message to user {user_id}: {e}")

    def send_error_notification(self, error_message):
        """
        Sends an error notification to the administrator.
        """
        try:
            self.notify_admin(f"❌ Error occurred: {error_message}")
        except Exception as e:
            print(f"Error sending error notification to admin: {e}")

    @staticmethod
    def fetch_privacy_policy(lang):
        """
        Fetches the privacy policy text for the specified language from environment variables.

        :param lang: Language code (e.g., 'ru', 'kz', 'en').
        :return: Text of the privacy policy or a fallback message if unavailable.
        """
        # Map language codes to environment variables.
        policies = {
            "ru": os.getenv("PRIVACY_POLICY_RU"),
            "kz": os.getenv("PRIVACY_POLICY_KZ"),
            "en": os.getenv("PRIVACY_POLICY_EN")
        }

        # Get the policy text based on the language, default to English if not set.
        policy_text = policies.get(lang, policies["en"])

        # Return a fallback message if the policy text is not found.
        if not policy_text:
            return "Privacy policy is currently unavailable. Please try again later."

        # Return the policy text.
        return policy_text
