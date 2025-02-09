import shared.telegram_bot.globals as globs
from shared.telegram_bot.logger import logger
from shared.telegram_bot.config import Config
from telegram import Bot

class Utils:
    """
    A utility class that encapsulates various helper methods to interact with the Telegram API.
    This includes sending messages to users or admins, and fetching the privacy policy link.

    The class uses lazy initialization of the 'self.bot' attribute to avoid scenarios
    where the bot is still None if 'globals.telegram_bot' has not yet been initialized.
    """

    def __init__(self):
        """
        Initializes the Utils instance with a None bot reference and sets the admin chat ID.
        The actual Bot object is obtained later by calling '_get_bot()'.
        """
        self.bot = None
        self.admin_chat_id = Config.ADMIN_CHAT_ID

    def _get_bot(self):
        """
        Lazily obtains or creates a Bot instance. If 'self.bot' is already set, returns it.
        Otherwise, tries to use 'globs.telegram_bot' (if available). If neither is set,
        creates a new Bot instance using TELEGRAM_BOT_TOKEN.

        Returns:
            Bot: A valid Bot instance that can be used to send Telegram messages.
        """
        if not self.bot:
            if globs.telegram_bot:
                # If the global telegram_bot is initialized in bootstrap, use it.
                self.bot = globs.telegram_bot
            else:
                # If no global bot is available yet, create a new one.
                logger.warning("Creating a new Bot instance because globs.telegram_bot is None.")
                self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        return self.bot

    def notify_admin(self, message: str):
        """
        Sends a message to the admin chat for critical notifications or announcements.

        Args:
            message (str): The text message to be sent to the admin.
        """
        try:
            bot = self._get_bot()  # Perform lazy initialization if necessary.
            bot.send_message(chat_id=self.admin_chat_id, text=message)
        except Exception as e:
            logger.error(f"Error sending notification to admin: {e}", exc_info=True)

    def notify_admin_group(self, message: str, admin_group_chat_id: str):
        """
        Sends a message to the specified admin group chat for notifications or updates.

        Args:
            message (str): The text message to be sent to the admin group.
            admin_group_chat_id (str): The chat ID of the admin group.
        """
        try:
            bot = self._get_bot()
            bot.send_message(chat_id=admin_group_chat_id, text=message)
        except Exception as e:
            logger.error(f"Error sending notification to admin group: {e}", exc_info=True)

    def send_user_message(self, user_id: str, message: str):
        """
        Sends a text message to a specific Telegram user.

        Args:
            user_id (str): The Telegram user ID as a string.
            message (str): The content of the text message.
        """
        try:
            bot = self._get_bot()
            bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f"Error sending message to user {user_id}: {e}", exc_info=True)

    def send_error_notification(self, error_message: str):
        """
        Sends an error notification to the admin, allowing them to track important issues in real time.

        Args:
            error_message (str): A descriptive message explaining the error.
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
            str: A formatted string containing the link to the privacy policy or an error message if missing.
        """
        # Get the privacy policy URL based on the selected language.
        policy_url = Config.get_privacy_policy_url(lang)
        if not policy_url:
            # Return a localized error message if no URL is found.
            return localization.get_string(lang, "error_message")

        # Retrieve the localized link text.
        link_text = localization.get_string(lang, "privacy_policy_link_text")
        # Return the formatted clickable link (Markdown link).
        return f"🔗[{link_text}]({policy_url})"
