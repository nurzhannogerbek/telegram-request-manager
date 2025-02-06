from telegram import Update
from telegram.ext import Application
from shared.telegram_bot.bootstrap import Bootstrap

class TelegramBot:
    def __init__(self, token):
        self.application = Application.builder().token(token).build()
        handlers = Bootstrap.get_telegram_bot().application.handlers
        handlers.setup(self.application)

    async def process_update(self, update_data):
        update = Update.de_json(update_data, self.application.bot)
        await self.application.process_update(update)
