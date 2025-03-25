import json
import asyncio
from shared.telegram_bot.logger import logger
from shared.telegram_bot.bootstrap import post_init_and_process

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
        # Parse the incoming event body as JSON to extract the Telegram update.
        update_data = json.loads(event["body"])

        # Fire-and-forget async processing to minimize cold start latency.
        asyncio.create_task(post_init_and_process(update_data))

        # Optional: add a short sleep to allow async task to start before Lambda exits.
        await asyncio.sleep(0.05)

        # Return a 200 OK response immediately to avoid Telegram retrying the update.
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Processing started."})
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
