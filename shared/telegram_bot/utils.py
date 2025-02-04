import os
import requests
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

        :param message: The message to send to the administrator.
        """
        try:
            # Use the bot to send a message to the admin's chat.
            self.bot.send_message(chat_id=self.admin_chat_id, text=message)
        except Exception as e:
            # Log any error encountered while sending the message.
            print(f"Error sending notification to admin: {e}")

    def notify_admin_group(self, message, admin_group_chat_id):
        """
        Sends a notification message to the admin group chat.

        :param message: The message to send to the admin group chat.
        :param admin_group_chat_id: The Telegram chat ID of the admin group.
        """
        try:
            # Send a message to the admin group chat.
            self.bot.send_message(chat_id=admin_group_chat_id, text=message)
        except Exception as e:
            # Log any error encountered while sending the message.
            print(f"Error sending notification to admin group: {e}")

    def send_user_message(self, user_id, message):
        """
        Sends a message to a specific user.

        :param user_id: The Telegram user ID of the recipient.
        :param message: The message to send to the user.
        """
        try:
            # Send a message to the specified user using their Telegram user ID.
            self.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            # Log any error encountered while sending the message.
            print(f"Error sending message to user {user_id}: {e}")

    def send_error_notification(self, error_message):
        """
        Sends an error notification to the administrator.

        :param error_message: The error message to notify the admin about.
        """
        try:
            # Notify the admin about the error by sending a message.
            self.notify_admin(f"❌ Error occurred: {error_message}")
        except Exception as e:
            # Log any error encountered while sending the error notification.
            print(f"Error sending error notification to admin: {e}")

    @staticmethod
    def fetch_privacy_policy(lang):
        """
        Fetches the privacy policy text for the specified language from an external source.

        :param lang: Language code (e.g., 'ru', 'kz', 'en').
        :return: Text of the privacy policy or a fallback message if unavailable.
        """
        # Define URLs for the privacy policies in different languages.
        policy_urls = {
            "ru": os.getenv("PRIVACY_POLICY_URL_RU"),  # URL for the Russian privacy policy.
            "kz": os.getenv("PRIVACY_POLICY_URL_KZ"),  # URL for the Kazakh privacy policy.
            "en": os.getenv("PRIVACY_POLICY_URL_EN")   # URL for the English privacy policy.
        }

        # Get the URL based on the language or default to the English policy if unavailable.
        url = policy_urls.get(lang, policy_urls["en"])
        if not url:
            # Return a fallback message if the URL is not set.
            return "Privacy policy URL is not configured for this language."

        try:
            # Send an HTTP GET request to fetch the privacy policy.
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception if the request fails.
            return response.text  # Return the fetched text of the privacy policy.
        except requests.RequestException as e:
            # Log any error encountered while fetching the privacy policy.
            print(f"Error fetching privacy policy for language '{lang}': {e}")
            # Return a fallback message if the request fails.
            return "Privacy policy is currently unavailable. Please try again later."
