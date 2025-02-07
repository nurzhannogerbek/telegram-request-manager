import logging

# Create a logger instance for the Telegram bot.
logger = logging.getLogger("telegram_bot")
# Set the logging level to INFO to capture general operational messages.
logger.setLevel(logging.INFO)

# Create a stream handler to output log messages to the console.
stream_handler = logging.StreamHandler()

# Define a log message format that includes the timestamp, log level, and message.
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# Attach the formatter to the stream handler.
stream_handler.setFormatter(formatter)

# Add the stream handler to the logger instance.
logger.addHandler(stream_handler)
