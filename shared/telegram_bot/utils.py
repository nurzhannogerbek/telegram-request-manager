from shared.telegram_bot.logger import logger
from shared.telegram_bot.config import Config
from shared.telegram_bot.globals import telegram_bot

class Utils:
    """
    Provides utility functions for sending messages, notifying administrators, and handling errors.
    Facilitates interactions with the Telegram API through reusable methods.
    """

    def __init__(self):
        """
        Initializes the Utils instance and assigns the Telegram bot and admin chat ID.
        """
        self.bot = telegram_bot  # Reference to the global Telegram bot instance.
        self.admin_chat_id = Config.ADMIN_CHAT_ID  # Admin chat ID for critical notifications.

    def notify_admin(self, message):
        """
        Sends a message to the admin chat to notify about important events or errors.

        Args:
            message (str): The message to be sent to the admin.
        """
        try:
            # Send the message to the admin chat using the Telegram bot.
            self.bot.send_message(chat_id=self.admin_chat_id, text=message)
        except Exception as e:
            # Log the error if the message fails to send.
            logger.error(f"Error sending notification to admin: {e}", exc_info=True)

    def notify_admin_group(self, message, admin_group_chat_id):
        """
        Sends a message to the admin group chat to provide notifications or updates.

        Args:
            message (str): The message to be sent.
            admin_group_chat_id (str): The chat ID of the admin group.
        """
        try:
            # Send the message to the admin group using the Telegram bot.
            self.bot.send_message(chat_id=admin_group_chat_id, text=message)
        except Exception as e:
            # Log the error if the message fails to send.
            logger.error(f"Error sending notification to admin group: {e}", exc_info=True)

    def send_user_message(self, user_id, message):
        """
        Sends a message to a specific user via the Telegram bot.

        Args:
            user_id (str): The Telegram user ID.
            message (str): The message to be sent.
        """
        try:
            # Send the message to the user.
            self.bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            # Log the error if the message fails to send.
            logger.error(f"Error sending message to user {user_id}: {e}", exc_info=True)

    def send_error_notification(self, error_message):
        """
        Sends a notification to the admin when an error occurs in the system.

        Args:
            error_message (str): The error message to be sent.
        """
        try:
            # Notify the admin about the error using the standard notification mechanism.
            self.notify_admin(f"❌ Error occurred: {error_message}")
        except Exception as e:
            # Log any errors encountered during the notification process.
            logger.error(f"Error sending error notification to admin: {e}", exc_info=True)

    @staticmethod
    def fetch_privacy_policy(lang, localization):
        """
        Retrieves the privacy policy URL for the specified language and formats it as a clickable link.

        Args:
            lang (str): The language code (e.g., 'en', 'ru', 'kz').
            localization (Localization): The localization object for retrieving strings.

        Returns:
            str: A formatted string containing the link to the privacy policy.
        """
        # Get the privacy policy URL based on the selected language.
        policy_url = Config.get_privacy_policy_url(lang)
        if not policy_url:
            # Return a localized error message if no URL is found.
            return localization.get_string(lang, "error_message")

        # Retrieve the localized link text.
        link_text = localization.get_string(lang, "privacy_policy_link_text")
        # Return the formatted clickable link.
        return f"🔗[{link_text}]({policy_url})"
