import json
import asyncio
from telegram import Update
from shared.telegram_bot.globals import application
from shared.telegram_bot.logger import logger

async def async_lambda_handler(event):
    try:
        update_data = json.loads(event["body"])
        update = Update.de_json(update_data, application.bot)
        await application.process_update(update)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Update processed successfully."})
        }
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}. Event: {event}")
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Invalid JSON payload."})
        }
    except Exception as e:
        logger.error(f"Unexpected error processing event: {event}. Error: {e}", exc_info=True)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Internal server error occurred."})
        }

def lambda_handler(event, context):
    return asyncio.run(async_lambda_handler(event))
