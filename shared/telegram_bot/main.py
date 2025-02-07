from shared.telegram_bot.globals import application
from telegram import Update


class TelegramBot:
    """
    Manages the processing of Telegram updates by interfacing with the global application instance.
    Encapsulates the logic for handling updates and passing them to the appropriate handlers.
    """

    def __init__(self):
        """
        Initializes the TelegramBot instance and assigns the global application instance.
        The application manages handlers and interactions with the Telegram API.
        """
        self.application = application

    async def process_update(self, update_data):
        """
        Processes an incoming Telegram update by converting it to an Update object
        and passing it to the application's update processing mechanism.

        Args:
            update_data (dict): The raw update data received from Telegram.

        Raises:
            Exception: If there are issues during update processing.
        """
        # Deserialize the raw update data into a Telegram Update object.
        update = Update.de_json(update_data, self.application.bot)

        # Pass the update to the application for processing through registered handlers.
        await self.application.process_update(update)
