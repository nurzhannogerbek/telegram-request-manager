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
    def fetch_privacy_policy(lang, localization):
        """
        Fetches the privacy policy URL for the specified language from environment variables
        and returns it as a properly formatted Markdown link.

        :param lang: Language code (e.g., 'ru', 'kz', 'en').
        :param localization: Localization instance to get the translated link text.
        :return: Formatted URL text of the privacy policy or a fallback message if unavailable.
        """
        # Map language codes to corresponding environment variables containing URLs.
        policy_urls = {
            "ru": os.getenv("PRIVACY_POLICY_URL_RU"),
            "kz": os.getenv("PRIVACY_POLICY_URL_KZ"),
            "en": os.getenv("PRIVACY_POLICY_URL_EN")
        }

        # Retrieve the URL based on the selected language, default to English if not set.
        policy_url = policy_urls.get(lang, policy_urls["en"])

        # If no valid URL is found, return a fallback message.
        if not policy_url:
            return localization.get_string(lang, "error_message")  # Use localized fallback message.

        # Retrieve localized link text from localization.
        link_text = localization.get_string(lang, "privacy_policy_link_text")

        # Return the URL formatted as a Markdown clickable link.
        return f"🔗[{link_text}]({policy_url})"
