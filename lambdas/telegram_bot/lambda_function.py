import json
import asyncio
from telegram import Update
from shared.telegram_bot.globals import application
from shared.telegram_bot.logger import logger
from shared.telegram_bot.handlers import BotHandlers

async def async_lambda_handler(event):
    logger.info("Lambda synchronous handler started. Passing to async handler.")
    try:
        logger.info("Registering BotHandlers now.")
        handlers = BotHandlers()
        handlers.setup(application)

        logger.info("Calling application.initialize().")
        await application.initialize()

        logger.info("Parsing event body as update.")
        update_data = json.loads(event["body"])
        update = Update.de_json(update_data, application.bot)
        logger.info(f"Parsed Update: {update.to_dict()}")

        logger.info("About to process update with application.")
        await application.process_update(update)

        logger.info("Successfully processed update. Returning 200 OK.")
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
    logger.info("Lambda synchronous handler started.")
    return asyncio.run(async_lambda_handler(event))
