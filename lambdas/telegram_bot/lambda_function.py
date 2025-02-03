import os
import json
from shared.telegram_bot.main import TelegramBot


def lambda_handler(event, context):
    """
    Entry point for the AWS Lambda function handling Telegram webhooks.
    Processes the incoming update and routes it to the bot's update handler.

    :param event: Event data passed by the Lambda trigger (Telegram API).
    :param context: Runtime information for the Lambda function.
    """
    # Initialize variables.
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")

    # Initialize bot instance.
    bot = TelegramBot(token)

    try:
        # Parse the incoming event as a Telegram update.
        update = json.loads(event["body"])
        bot.process_update(update)

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
