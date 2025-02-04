import os
import json
import asyncio
from shared.telegram_bot.main import TelegramBot

# Create a global instance of the bot for reuse across requests
bot_instance = TelegramBot(os.getenv("TELEGRAM_BOT_TOKEN"))

async def async_lambda_handler(event):
    """
    Asynchronous entry point for handling Telegram updates in AWS Lambda.
    :param event: The event data passed by the Lambda trigger.
    """
    try:
        # Parse the incoming event as a Telegram update.
        update = json.loads(event["body"])

        # Process the update using the bot instance.
        await bot_instance.application.process_update(update)

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
    # Ensure that the asynchronous handler is correctly executed.
    return asyncio.run(async_lambda_handler(event))
