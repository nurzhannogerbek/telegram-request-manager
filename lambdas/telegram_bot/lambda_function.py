import os
import json
import asyncio
from telegram import Update
from shared.telegram_bot.main import TelegramBot

# Initialize the bot globally.
token = os.getenv("TELEGRAM_BOT_TOKEN")
if not token:
    raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")
bot = TelegramBot(token)

async def async_lambda_handler(event):
    """
    Asynchronous entry point for handling Telegram updates in AWS Lambda.
    :param event: The event data passed by the Lambda trigger.
    """
    try:
        # Parse the incoming event as a Telegram update.
        update_data = json.loads(event["body"])
        update = Update.de_json(update_data, bot.application.bot)

        # Initialize the application and process the update.
        await bot.application.initialize()
        await bot.application.process_update(update)

        # Return HTTP 200 (success response) to Telegram.
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Update processed successfully."})
        }

    except Exception as e:
        # Log the error for debugging purposes.
        print(f"Error processing Telegram update: {e}")

        # Respond with HTTP 200 to prevent retries from Telegram.
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Error occurred, but acknowledged to prevent retries."})
        }

def lambda_handler(event, context):
    """
    Synchronous entry point for AWS Lambda, runs the asynchronous handler.
    """
    return asyncio.run(async_lambda_handler(event))
