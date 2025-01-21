from telegram import Bot
import os

class Utils:
    """
    Class to handle utility functions for the bot.
    """

    def __init__(self):
        """
        Initializes the utility class with environment variables.
        """
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.bot_token:
            raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")

        self.admin_chat_id = os.getenv("ADMIN_CHAT_ID")
        if not self.admin_chat_id:
            raise EnvironmentError("ADMIN_CHAT_ID environment variable is not set.")

        self.bot = Bot(token=self.bot_token)

    def notify_admin(self, message):
        """
        Sends a notification to the administrator's Telegram chat.

        :param message: The message to send to the administrator.
        """
        try:
            self.bot.send_message(chat_id=self.admin_chat_id, text=message)
        except Exception as e:
            print(f"Error sending notification to admin: {e}")
