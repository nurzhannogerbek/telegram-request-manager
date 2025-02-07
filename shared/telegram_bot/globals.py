from telegram.ext import Application
from telegram import Bot

# Global variables to hold the application and bot instances.
# These are reused during AWS Lambda hot starts to avoid reinitialization and improve performance.
application: Application | None = None  # Holds the global Telegram Application instance.
telegram_bot: Bot | None = None  # Holds the global Telegram Bot instance.
