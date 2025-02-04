import logging
from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.google_sheets import GoogleSheets
from shared.telegram_bot.utils import Utils

# Configure logging to track bot activities and errors (if needed in future)
logging.basicConfig(level=logging.INFO)

class BotHandlers:
    """
    Class to manage all bot command and message handlers.
    """

    def __init__(self):
        """
        Initializes required components for handling user interactions, localization,
        Google Sheets integration, and utility functions.
        """
        self.user_forms = {}  # Stores active user forms and language preferences keyed by user ID.
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
            print(f"User {user_id} issued the /start command.")  # Log the start command.

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
            print(f"Error in start handler: {e}")

    async def set_language(self, update, context):
        """
        Sets the user's language based on their selection and sends the privacy policy.
        """
        query = update.callback_query  # Extract the callback query object.
        await query.answer()  # Acknowledge the callback query.

        try:
            user_id = query.from_user.id  # Get user ID from the query object.
            lang = query.data.split("_")[1]  # Extract the selected language code.

            print(f"User {user_id} selected language: {lang}.")  # Log the language selection.

            # Store the selected language in self.user_forms
            self.user_forms[user_id] = {"lang": lang}

            # Send the privacy policy using the selected language.
            await self.send_privacy_policy(update, context)

        except Exception as e:
            print(f"Error in set_language handler: {e}")

    async def send_privacy_policy(self, update, context):
        """
        Sends the privacy policy link to the user and asks for their consent using inline buttons.

        :param update: The Telegram update object, containing details of the incoming message or query.
        :param context: The context object, providing access to user-specific data and bot configuration.
        """
        try:
            # Extract the user ID from either a callback query or message, depending on how the function was triggered.
            user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
            lang = self.user_forms.get(user_id, {}).get("lang", "en")  # Retrieve the selected language.

            print(f"Sending privacy policy to user {user_id} in language '{lang}'.")

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

            # Send the message depending on how the function was triggered.
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
            print(f"Error in send_privacy_policy handler: {e}")

    async def handle_privacy_response(self, update, context):
        """
        Handles the user's response to the privacy policy.
        """
        query = update.callback_query
        await query.answer()

        try:
            user_id = query.from_user.id
            lang = self.user_forms.get(user_id, {}).get("lang", "en")  # Retrieve the selected language.

            print(f"User {user_id} responded to privacy policy in language '{lang}'.")

            if query.data == "privacy_accept":
                print(f"User {user_id} accepted the privacy policy.")

                # Initialize a new application form and store it in user_forms.
                form = ApplicationForm(lang, self.localization)
                self.user_forms[user_id] = {"form": form, "lang": lang}

                # Get the first question.
                question = form.get_next_question()
                start_message = self.localization.get_string(lang, "start_questionnaire")

                print(f"First question for user {user_id}: {question}")
                await query.edit_message_text(f"{start_message} {question}")

            elif query.data == "privacy_decline":
                print(f"User {user_id} declined the privacy policy.")
                decline_message = self.localization.get_string(lang, "decline_message")
                await query.edit_message_text(decline_message)

        except Exception as e:
            print(f"Error in handle_privacy_response handler: {e}")

    async def handle_response(self, update, context):
        """
        Processes user responses and manages the application form flow.
        """
        try:
            user_id = update.message.from_user.id
            user_data = self.user_forms.get(user_id)

            if not user_data:
                print(f"User {user_id} tried to respond without starting the form.")
                await update.message.reply_text(self.localization.get_string("en", "error_message"))
                return

            lang = user_data.get("lang", "en")
            form = user_data.get("form")

            if not form:
                print(f"User {user_id} tried to respond without an active form.")
                await update.message.reply_text(self.localization.get_string(lang, "error_message"))
                return

            print(f"Saving response from user {user_id}: {update.message.text}")
            form.save_response(update.message.text)

            if form.is_complete():
                print(f"User {user_id} completed the form.")
                self.google_sheets.save_to_sheet(user_id, form.get_all_responses())
                await update.message.reply_text(self.localization.get_string(lang, "application_complete"))
                del self.user_forms[user_id]  # Clean up the form data.
            else:
                next_question = form.get_next_question()
                print(f"Asking next question to user {user_id}: {next_question}")
                await update.message.reply_text(next_question)

        except Exception as e:
            print(f"Error in handle_response handler: {e}")

    async def handle_join_request(self, update: Update, context):
        """
        Handles new join requests and starts the onboarding process by sending a multilingual welcome message.
        """
        try:
            join_request = update.chat_join_request
            user_id = join_request.from_user.id
            print(f"Received join request from user {user_id}.")
            await self.start(update, context)

        except Exception as e:
            print(f"Error in handle_join_request handler: {e}")

    async def approve_join_request(self, user_id, context):
        """
        Automatically approves the join request after the user completes the application.
        """
        try:
            print(f"Approving join request for user {user_id}.")
            await context.bot.approve_chat_join_request(chat_id=context.chat_data["chat_id"], user_id=user_id)
            await self.utils.notify_admin(f"✅ User {user_id} has been approved to join the group.")

        except Exception as e:
            print(f"Error in approve_join_request handler: {e}")

    def setup(self, application):
        """
        Registers all command, message, and join request handlers with the application.
        """
        print("Setting up command and message handlers.")
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_privacy_response, pattern="^privacy_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        application.add_handler(ChatJoinRequestHandler(self.handle_join_request))
