import json
import asyncio
from telegram import Update
from shared.telegram_bot.logger import logger
from shared.telegram_bot.bootstrap import ensure_application_ready
import shared.telegram_bot.globals as globs


async def async_lambda_handler(event):
    """
    Handles asynchronous processing of incoming Telegram updates via AWS Lambda.

    Args:
        event (dict): The AWS Lambda event containing the update payload from Telegram.
            - event["body"]: A JSON string representing the Telegram update.

    Returns:
        dict: A dictionary containing the HTTP response with a status code and message.
    """
    # Ensure that the application is fully initialized and ready to handle updates.
    await ensure_application_ready()
    # Initialize the application context if necessary.
    await globs.application.initialize()

    try:
        # Parse the incoming event body as JSON to extract update data from Telegram.
        update_data = json.loads(event["body"])
        # Convert the parsed update data to a Telegram Update object.
        update = Update.de_json(update_data, globs.application.bot)

        # Pass the update to the application's update processing logic.
        await globs.application.process_update(update)

        # Return a successful HTTP response indicating that the update was processed.
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Update processed successfully."})
        }

    except json.JSONDecodeError as e:
        # Handle cases where the event body is not valid JSON.
        logger.error(f"JSON decoding error: {e}. Event: {event}")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Invalid JSON payload."})
        }

    except Exception as e:
        # Catch any unexpected errors that occur during processing and log them.
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Internal server error occurred."})
        }


def lambda_handler(event, context):
    """
    Entry point for the AWS Lambda function.
    Triggers the asynchronous handler to process incoming Telegram updates.

    Args:
        event (dict): The AWS Lambda event containing the update payload from Telegram.
        context (object): The AWS Lambda context object (unused in this implementation).

    Returns:
        dict: The HTTP response returned by the asynchronous handler.
    """
    # Entry point for the AWS Lambda function.
    # It triggers the asynchronous handler to process incoming Telegram updates.
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_lambda_handler(event))