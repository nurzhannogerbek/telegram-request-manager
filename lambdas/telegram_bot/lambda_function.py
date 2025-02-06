import json
import asyncio
from telegram import Update
from shared.telegram_bot.bootstrap import Bootstrap
from shared.telegram_bot.logger import logger

global_telegram_bot = Bootstrap.get_telegram_bot()

async def async_lambda_handler(event):
    try:
        update_data = json.loads(event["body"])
        update = Update.de_json(update_data, global_telegram_bot.application.bot)
        await global_telegram_bot.application.process_update(update)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Update processed successfully."})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Error occurred, logged internally."})
        }

def lambda_handler(event, context):
    return asyncio.run(async_lambda_handler(event))
