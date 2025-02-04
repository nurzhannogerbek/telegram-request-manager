import re
import logging
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils

# Configure logging to track bot activities and errors.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BotHandlers:
    """
    Class to manage all bot command and message handlers.
    """

    def __init__(self):
        """
        Initializes required components for handling user interactions, localization,
        Google Sheets integration, and utility functions.
        """
        self.user_forms = {}  # Stores active user forms keyed by user ID.
        self.localization = Localization()  # Handles localization for user interactions.
        self.google_sheets = GoogleSheets()  # Manages Google Sheets for storing user data.
        self.utils = Utils()  # Provides utility functions like admin notifications.

    async def start(self, update, context):
        """
        Handles the /start command to initialize language selection.
        Sends a multilingual welcome message with inline buttons for the user to choose their preferred language.
        """
        try:
            user_id = update.effective_user.id  # Get user ID from the update object.
            logger.info(f"User {user_id} issued the /start command.")  # Log the start command.

            # Display language options as inline buttons.
            keyboard = [[
                InlineKeyboardButton("Русский", callback_data="lang_ru"),
                InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
                InlineKeyboardButton("English", callback_data="lang_en")
            ]]

            # Send the multilingual welcome message.
            await context.bot.send_message(
                chat_id=user_id,
                text=self.localization.get_multilang_welcome_message(),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error in start handler: {e}")

    async def set_language(self, update, context):
        """
        Sets the user's language based on their selection and sends the privacy policy.
        """
        query = update.callback_query  # Extract the callback query object.
        await query.answer()  # Acknowledge the callback query.

        try:
            user_id = query.from_user.id  # Get user ID from the query object.
            lang = query.data.split("_")[1]  # Extract the selected language code.

            logger.info(f"User {user_id} selected language: {lang}.")  # Log the language selection.

            # Store the selected language for the user in the context.
            context.user_data["lang"] = lang

            # Send the privacy policy using the correct language.
            await self.send_privacy_policy(update, context)

        except Exception as e:
            logger.error(f"Error in set_language handler: {e}")

    async def send_privacy_policy(self, update, context):
        """
        Sends the privacy policy link to the user and asks for their consent using inline buttons.

        :param update: The Telegram update object, containing details of the incoming message or query.
        :param context: The context object, providing access to user-specific data and bot configuration.
        """
        try:
            # Extract the user ID from either a callback query or message, depending on how the function was triggered.
            user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id

            # Retrieve the user's preferred language from the context. Defaults to 'en' if not set.
            lang = context.user_data.get("lang", "en")

            logger.info(f"Sending privacy policy to user {user_id} in language '{lang}'.")

            # Retrieve the URL of the privacy policy as a clickable link using the localized text.
            privacy_policy_link = self.utils.fetch_privacy_policy(lang, self.localization)

            # Retrieve button and prompt texts for the chosen language.
            accept_button = self.localization.get_string(lang, "privacy_accept")
            decline_button = self.localization.get_string(lang, "privacy_decline")
            prompt_text = self.localization.get_string(lang, "privacy_prompt")

            # Construct the message content by combining the prompt and the clickable link to the policy.
            message_text = f"{prompt_text}\n\n{privacy_policy_link}"

            # Build the inline keyboard with buttons for user responses.
            keyboard = [
                [
                    InlineKeyboardButton(accept_button, callback_data="privacy_accept"),
                    InlineKeyboardButton(decline_button, callback_data="privacy_decline")
                ]
            ]

            # Check how the function was triggered and send or edit the appropriate message.
            if update.callback_query:
                # Edit the existing message when triggered by a callback query.
                await update.callback_query.edit_message_text(
                    text=message_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )
            else:
                # Send a new message when triggered by a regular message.
                await update.message.reply_text(
                    text=message_text,
                    reply_markup=InlineKeyboardMarkup(keyboard),
                    parse_mode="Markdown"
                )

        except Exception as e:
            # Log any errors encountered during the process for debugging and analysis.
            logger.error(f"Error in send_privacy_policy handler: {e}")

    async def handle_privacy_response(self, update, context):
        """
        Handles the user's response to the privacy policy.
        """
        query = update.callback_query  # Extract the callback query object.
        await query.answer()  # Acknowledge the response.

        try:
            user_id = query.from_user.id  # Get user ID from the query object.
            lang = context.user_data.get("lang", "en")  # Default to English if not set.

            if query.data == "privacy_accept":
                logger.info(f"User {user_id} accepted the privacy policy.")  # Log acceptance.

                # Initialize a new application form for the user.
                self.user_forms[user_id] = ApplicationForm(lang, self.localization)
                question = self.user_forms[user_id].get_next_question()
                start_message = self.localization.get_string(lang, "start_questionnaire")

                # Log form initialization for debugging purposes.
                logger.info(f"Form initialized for user {user_id}. First question: {question}")

                # Send the first question of the form.
                await query.edit_message_text(f"{start_message} {question}")

            elif query.data == "privacy_decline":
                logger.info(f"User {user_id} declined the privacy policy.")  # Log decline.

                # Send a message indicating that the dialog is closed.
                decline_message = self.localization.get_string(lang, "decline_message")
                await query.edit_message_text(decline_message)

        except Exception as e:
            logger.error(f"Error in handle_privacy_response handler: {e}")

    async def handle_response(self, update, context):
        """
        Processes user responses and manages the application form flow.
        """
        try:
            user_id = update.message.from_user.id  # Extract the user ID from the update object.
            lang = context.user_data.get("lang", "en")  # Get the user's selected language.
            form = self.user_forms.get(user_id)  # Retrieve the active form for the user.

            if not form:
                logger.warning(f"User {user_id} tried to respond without starting the form.")  # Log the warning.
                await update.message.reply_text(self.localization.get_string(lang, "error_message"))
                return

            logger.info(f"Saving response from user {user_id}: {update.message.text}.")  # Log the response.

            # Save the user's response to the current question.
            form.save_response(update.message.text)

            if form.is_complete():
                logger.info(f"User {user_id} completed the form. Saving responses to Google Sheets.")  # Log completion.

                # Save responses to Google Sheets.
                self.google_sheets.save_to_sheet(user_id, form.responses)
                complete_message = self.localization.get_string(lang, "application_complete")

                # Notify the user of successful form submission.
                await update.message.reply_text(complete_message)
                del self.user_forms[user_id]  # Clean up the form.

                # Approve the join request automatically.
                await self.approve_join_request(user_id, context)
            else:
                # Ask the next question in the form.
                next_question = form.get_next_question()
                logger.info(f"Asking the next question to user {user_id}.")  # Log the next question.
                await update.message.reply_text(next_question)

        except Exception as e:
            logger.error(f"Error in handle_response handler: {e}")

    async def handle_join_request(self, update: Update, context):
        """
        Handles new join requests and starts the onboarding process by sending a multilingual welcome message.
        """
        try:
            join_request = update.chat_join_request  # Extract the join request object.
            user_id = join_request.from_user.id  # Extract the user ID.
            logger.info(f"Received join request from user {user_id}.")  # Log the join request.

            # Proceed to the language selection step.
            await self.start(update, context)

        except Exception as e:
            logger.error(f"Error in handle_join_request handler: {e}")

    async def approve_join_request(self, user_id, context):
        """
        Automatically approves the join request after the user completes the application.
        """
        try:
            logger.info(f"Approving join request for user {user_id}.")  # Log the approval action.

            # Approve the join request.
            await context.bot.approve_chat_join_request(chat_id=context.chat_data["chat_id"], user_id=user_id)
            await self.utils.notify_admin(f"✅ User {user_id} has been approved to join the group.")

        except Exception as e:
            logger.error(f"Error in approve_join_request handler: {e}")

    def setup(self, application):
        """
        Registers all command, message, and join request handlers with the application.
        """
        logger.info("Setting up command and message handlers.")  # Log the setup process.

        # Register handlers for bot commands and updates.
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_privacy_response, pattern="^privacy_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
