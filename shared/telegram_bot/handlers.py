from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.validation import Validation
from shared.telegram_bot.logger import logger
from shared.telegram_bot.globals import telegram_bot
from shared.telegram_bot.bootstrap import Bootstrap

class BotHandlers:
    def __init__(self):
        logger.info("Initializing BotHandlers.")
        self.user_forms = {}
        self.localization = Localization()
        self.google_sheets = Bootstrap.get_google_sheets()
        self.utils = Bootstrap.get_utils()
        self.bot = telegram_bot

    async def start(self, update, context):
        logger.info("start handler invoked.")
        try:
            user_id = update.effective_user.id
            logger.info(f"start handler: user_id={user_id}")
            keyboard = [
                [
                    InlineKeyboardButton("Русский", callback_data="lang_ru"),
                    InlineKeyboardButton("Қазақша", callback_data="lang_kz"),
                    InlineKeyboardButton("English", callback_data="lang_en")
                ]
            ]
            await self.bot.send_message(
                chat_id=user_id,
                text=self.localization.get_multilang_welcome_message(),
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            logger.error(f"Error in start handler: {e}", exc_info=True)

    async def set_language(self, update, context):
        logger.info("set_language invoked.")
        query = update.callback_query
        await query.answer()
        try:
            user_id = query.from_user.id
            logger.info(f"User {user_id} chose language.")
            lang = query.data.split("_")[1]
            context.user_data["lang"] = lang
            chat_id = self.google_sheets.get_chat_id(user_id)
            self._save_user_state(user_id, lang, 0, {}, chat_id)
            await self.send_privacy_policy(update, context)
        except Exception as e:
            logger.error(f"Error in set_language handler: {e}", exc_info=True)

    async def send_privacy_policy(self, update, context):
        logger.info("send_privacy_policy invoked.")
        try:
            user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
            logger.info(f"Sending privacy policy to user {user_id}")
            lang = context.user_data.get("lang") or self.google_sheets.get_user_state(user_id)[0]
            privacy_policy_link = self.utils.fetch_privacy_policy(lang, self.localization)
            message_text = f"{self.localization.get_string(lang, 'privacy_prompt')}\n\n{privacy_policy_link}"
            keyboard = [
                [
                    InlineKeyboardButton(self.localization.get_string(lang, "privacy_accept"), callback_data="privacy_accept"),
                    InlineKeyboardButton(self.localization.get_string(lang, "privacy_decline"), callback_data="privacy_decline")
                ]
            ]
            if update.callback_query:
                logger.info(f"Editing existing message with privacy policy for user {user_id}")
                await update.callback_query.edit_message_text(
                    text=message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
                )
            else:
                logger.info(f"Sending new message with privacy policy to user {user_id}")
                await self.bot.send_message(
                    chat_id=user_id, text=message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Error in send_privacy_policy handler: {e}", exc_info=True)

    async def handle_privacy_response(self, update, context):
        logger.info("handle_privacy_response invoked.")
        query = update.callback_query
        await query.answer()
        try:
            user_id = query.from_user.id
            logger.info(f"User {user_id} responded to privacy policy.")
            lang, current_question_index, responses, chat_id = self.google_sheets.get_user_state(user_id)
            if query.data == "privacy_accept":
                logger.info(f"User {user_id} accepted privacy policy.")
                form = ApplicationForm(lang, self.localization)
                form.current_question_index = current_question_index
                form.responses = responses
                self.user_forms[user_id] = form
                self._save_user_state(user_id, lang, form.current_question_index, form.responses, chat_id)
                await self._send_next_question(user_id)
            else:
                logger.info(f"User {user_id} declined privacy policy.")
                await query.edit_message_text(text=self.localization.get_string(lang, "decline_message"))
        except Exception as e:
            logger.error(f"Error in handle_privacy_response handler: {e}", exc_info=True)

    async def handle_response(self, update, context):
        logger.info("handle_response invoked.")
        try:
            user_id = update.message.from_user.id
            logger.info(f"User {user_id} responding to question.")
            form = self.user_forms.get(user_id)
            if not form:
                lang, current_question_index, responses, chat_id = self.google_sheets.get_user_state(user_id)
                if not lang:
                    logger.info(f"User {user_id} has no saved state, sending error_message.")
                    await update.message.reply_text(self.localization.get_string("en", "error_message"))
                    return
                logger.info(f"Recreating ApplicationForm for user {user_id} with lang={lang}.")
                form = ApplicationForm(lang, self.localization)
                form.current_question_index = current_question_index
                form.responses = responses
                self.user_forms[user_id] = form
            user_response = update.message.text.strip()
            if not await self._validate_and_handle_response(user_response, form, user_id):
                return
            if form.is_complete():
                logger.info(f"Form complete for user {user_id}. Saving to sheet.")
                self.google_sheets.save_to_sheet(user_id, form.get_all_responses())
                del self.user_forms[user_id]
                await update.message.reply_text(self.localization.get_string(form.lang, "application_complete"))
                await self.approve_join_request(user_id, context)
            else:
                logger.info(f"Form not yet complete for user {user_id}, sending next question.")
                await self._send_next_question(user_id)
        except Exception as e:
            logger.error(f"Error in handle_response handler: {e}", exc_info=True)

    async def handle_join_request(self, update, context):
        logger.info("handle_join_request invoked.")
        try:
            join_request = update.chat_join_request
            user_id = join_request.from_user.id
            chat_id = join_request.chat.id
            logger.info(f"chat_join_request for user {user_id} in chat {chat_id}")
            self._save_user_state(user_id, "", 0, {}, str(chat_id))
            logger.info("Calling self.start to send greeting message.")
            await self.start(update, context)
        except Exception as e:
            logger.error(f"Error in handle_join_request handler: {e}", exc_info=True)

    async def approve_join_request(self, user_id, context):
        logger.info(f"approve_join_request invoked for user {user_id}")
        try:
            _, _, _, chat_id = self.google_sheets.get_user_state(user_id)
            if not chat_id:
                logger.info(f"No chat_id found for user {user_id}, skipping approval.")
                return
            logger.info(f"Approving join request for user {user_id} in chat {chat_id}")
            await context.bot.approve_chat_join_request(chat_id=int(chat_id), user_id=user_id)
            await self.utils.notify_admin(f"✅ User {user_id} has been approved.")
        except Exception as e:
            logger.error(f"Error in approve_join_request handler: {e}", exc_info=True)

    def setup(self, application):
        logger.info("BotHandlers.setup called, registering handlers.")
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_privacy_response, pattern="^privacy_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        application.add_handler(ChatJoinRequestHandler(self.handle_join_request))

    def _save_user_state(self, user_id, lang, current_question_index, responses, chat_id):
        logger.info(f"_save_user_state: user_id={user_id}, lang={lang}, cqi={current_question_index}, chat_id={chat_id}")
        self.google_sheets.save_user_state(user_id, lang, current_question_index, responses, chat_id)

    async def _send_next_question(self, user_id):
        logger.info(f"_send_next_question invoked for user {user_id}")
        form = self.user_forms.get(user_id)
        next_question = form.get_next_question() if form else None
        if next_question:
            logger.info(f"Next question for user {user_id} is: {next_question}")
            self._save_user_state(user_id, form.lang, form.current_question_index, form.responses, self.google_sheets.get_chat_id(user_id))
            await self.bot.send_message(chat_id=user_id, text=next_question)
        else:
            logger.info(f"No more questions for user {user_id}")

    async def _validate_and_handle_response(self, user_response, form, user_id):
        logger.info(f"_validate_and_handle_response for user {user_id}, response={user_response}")
        current_question_type = form.get_current_question_type()
        logger.info(f"Current question type for user {user_id}: {current_question_type}")
        if current_question_type == "email" and not Validation.validate_email(user_response):
            logger.info(f"User {user_id} failed email validation.")
            await self.bot.send_message(chat_id=user_id, text=self.localization.get_string(form.lang, "invalid_email"))
            return False
        if current_question_type == "phone" and not Validation.validate_phone(user_response):
            logger.info(f"User {user_id} failed phone validation.")
            await self.bot.send_message(chat_id=user_id, text=self.localization.get_string(form.lang, "invalid_phone"))
            return False
        if current_question_type == "age" and not Validation.validate_age(user_response):
            logger.info(f"User {user_id} failed age validation.")
            await self.bot.send_message(chat_id=user_id, text=self.localization.get_string(form.lang, "invalid_age"))
            return False
        form.save_response(user_response)
        return True
