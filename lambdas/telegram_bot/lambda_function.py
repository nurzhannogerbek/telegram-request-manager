import os
import json
from telegram import Update
from shared.telegram_bot.main import TelegramBot

def lambda_handler(event, context):
    """
    AWS Lambda handler function to process incoming events from Telegram via a webhook.

    :param event: Event data passed to the Lambda function.
    :param context: Context data passed to the Lambda function.
    :return: HTTP response with status code and message.
    """
    try:
        # Get the bot token from environment variables.
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not token:
            raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")

        # Ensure the event contains a valid Telegram update.
        if "body" not in event:
            raise ValueError("No valid Telegram update found in the event payload.")

        # Parse the incoming Telegram event (body).
        telegram_update = json.loads(event["body"])
        update = Update.de_json(telegram_update, None)  # Convert JSON to Telegram Update object.

        # Initialize the Telegram bot and process the update.
        bot = TelegramBot(token)
        # Process a single update using built-in method.
        bot.application.process_update(update)

        # Return 200 OK to prevent Telegram from retrying.
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Update processed successfully."})
        }

    except Exception as e:
        # Log the error for debugging purposes.
        print(f"Error processing Telegram update: {e}")

        # Return 200 OK to prevent retry loops from Telegram, but log the error internally.
        return {
            "statusCode": 200,
            "body": json.dumps({"message": f"An error occurred: {str(e)}"})
        }
