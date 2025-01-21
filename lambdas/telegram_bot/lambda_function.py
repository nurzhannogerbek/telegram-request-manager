import os
from shared.telegram_bot.main import TelegramBot


def lambda_handler(event, context):
    """
    AWS Lambda handler function to initialize and start the Telegram bot.

    This function serves as the entry point for the AWS Lambda function. It initializes
    the Telegram bot and starts polling for updates.

    :param event: Event data passed to the Lambda function.
    :param context: Context data passed to the Lambda function.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")

    # Initialize and start the Telegram bot.
    bot = TelegramBot(token)
    bot.run()
