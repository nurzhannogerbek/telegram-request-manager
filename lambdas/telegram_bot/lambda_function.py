import json
import asyncio
from telegram import Update
from shared.telegram_bot.logger import logger
from shared.telegram_bot.bootstrap import ensure_application_ready
import shared.telegram_bot.globals as globs

async def async_lambda_handler(event):
    logger.info("Lambda async handler start. Checking application readiness.")
    ensure_application_ready()
    logger.info("Initializing application if needed.")
    await globs.application.initialize()
    try:
        update_data = json.loads(event["body"])
        update = Update.de_json(update_data, globs.application.bot)
        logger.info(f"Parsed Update: {update.to_dict()}")
        logger.info("Processing update with application.")
        await globs.application.process_update(update)
        logger.info("Successfully processed update. Return 200.")
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
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Internal server error occurred."})
        }

def lambda_handler(event, context):
    logger.info("Lambda sync handler, calling async.")
    return asyncio.run(async_lambda_handler(event))
