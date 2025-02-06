from shared.telegram_bot.globals import application
from telegram import Update

class TelegramBot:
    def __init__(self):
        self.application = application

    async def process_update(self, update_data):
        update = Update.de_json(update_data, self.application.bot)
        await self.application.process_update(update)
