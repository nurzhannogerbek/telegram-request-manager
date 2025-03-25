import json
import asyncio
import shared.telegram_bot.globals as globs
from shared.telegram_bot.logger import logger
from shared.telegram_bot.bootstrap import post_init_and_process
from shared.telegram_bot.bootstrap import ensure_application_ready

async def async_lambda_handler(event):
    """
    Asynchronous handler for processing incoming Telegram updates via AWS Lambda.

    This function is optimized for cold starts by using fire-and-forget async task execution.
    It immediately returns a 200 OK response to Telegram while the actual update processing
    happens asynchronously in the background.

    Args:
        event (dict): The AWS Lambda event containing the update payload from Telegram.
            - event["body"]: A JSON string representing the Telegram update.

    Returns:
        dict: A dictionary containing the HTTP response with a status code and message.
    """
    try:
        # Initialize the application and bot.
        await ensure_application_ready()
        await globs.application.initialize()

        # Parse incoming update from Telegram.
        update_data = json.loads(event["body"])

        # Inspect update type to determine if it's a join request.
        if "chat_join_request" in update_data:
            # For join requests: await to ensure welcome message is sent.
            await post_init_and_process(update_data)
        else:
            # For all other updates: background execution.
            asyncio.create_task(post_init_and_process(update_data))

        # Immediately return HTTP 200 response to Telegram.
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Update received and processing started."})
        }
    except json.JSONDecodeError as e:
        # Handle cases where the incoming payload is not valid JSON.
        logger.error(f"JSON decoding error: {e}. Event: {event}")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Invalid JSON payload."})
        }
    except Exception as e:
        # Catch any unexpected errors that occur during processing and log them.
        logger.error(f"Unexpected error occurred during update processing: {e}", exc_info=True)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Internal server error occurred while processing the update."})
        }

def lambda_handler(event, context):
    """
    Entry point for the AWS Lambda function.

    This is a synchronous wrapper that invokes the asynchronous handler to process
    incoming Telegram updates from the webhook.

    Args:
        event (dict): The AWS Lambda event containing the update payload from Telegram.
        context (object): The AWS Lambda context object (not used in this implementation).

    Returns:
        dict: The HTTP response returned by the asynchronous handler.
    """
    # Run the asynchronous logic inside the existing or new event loop.
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(async_lambda_handler(event))
