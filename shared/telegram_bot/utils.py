import os
from telegram import Bot

class Utils:
    """
    Utility class for managing common bot-related functions such as notifications.
    """

    def __init__(self):
        """
        Initializes the utility class by loading environment variables for bot token
        and admin chat ID.
        """
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")  # Retrieves the bot token from environment variables.
        if not self.bot_token:
            raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")

        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")  # Retrieves the admin chat ID from environment variables.
        if not self.admin_chat_id:
            raise EnvironmentError("ADMIN_CHAT_ID environment variable is not set.")

        self.bot = Bot(token=self.bot_token)  # Initializes the Telegram bot instance.

    def notify_admin(self, message):
        """
        Sends a notification message to the administrator's Telegram chat.

        :param message: The message to send to the administrator.
        """
        try:
            self.bot.send_message(chat_id=self.admin_chat_id, text=message)  # Sends the message via Telegram bot.
        except Exception as e:
            print(f"Error sending notification to admin: {e}")  # Logs any error that occurs during notification.

    def notify_admin_group(self, message, admin_group_chat_id):
        """
        Sends a notification message to the admin group chat.

        :param message: The message to send to the admin group chat.
        :param admin_group_chat_id: The Telegram chat ID of the admin group.
        """
        try:
            self.bot.send_message(chat_id=admin_group_chat_id, text=message)  # Sends the message to the admin group.
        except Exception as e:
            print(f"Error sending notification to admin group: {e}")  # Logs any error that occurs.

    def send_user_message(self, user_id, message):
        """
        Sends a message to a specific user.

        :param user_id: The Telegram user ID of the recipient.
        :param message: The message to send to the user.
        """
        try:
            self.bot.send_message(chat_id=user_id, text=message)  # Sends the message to the specified user.
        except Exception as e:
            print(f"Error sending message to user {user_id}: {e}")  # Logs any error that occurs.

    def send_error_notification(self, error_message):
        """
        Sends an error notification to the administrator.

        :param error_message: The error message to notify the admin about.
        """
        try:
            self.notify_admin(f"❌ Error occurred: {error_message}")  # Notifies the admin of the error.
        except Exception as e:
            print(f"Error sending error notification to admin: {e}")  # Logs any additional error.
