from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, ChatJoinRequestHandler, filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from shared.telegram_bot.forms import ApplicationForm
from shared.telegram_bot.localization import Localization
from shared.telegram_bot.validation import Validation
from shared.telegram_bot.logger import logger
from shared.telegram_bot.globals import telegram_bot, google_sheets, utils

class BotHandlers:
    def __init__(self):
        self.user_forms = {}
        self.localization = Localization()
        self.google_sheets = google_sheets
        self.utils = utils
        self.bot = telegram_bot

    async def start(self, update, context):
        try:
            user_id = update.effective_user.id
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
        query = update.callback_query
        await query.answer()
        try:
            user_id = query.from_user.id
            lang = query.data.split("_")[1]
            context.user_data["lang"] = lang
            chat_id = self.google_sheets.get_chat_id(user_id)
            self._save_user_state(user_id, lang, 0, {}, chat_id)
            await self.send_privacy_policy(update, context)
        except Exception as e:
            logger.error(f"Error in set_language handler: {e}", exc_info=True)

    async def send_privacy_policy(self, update, context):
        try:
            user_id = update.callback_query.from_user.id if update.callback_query else update.message.from_user.id
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
                await update.callback_query.edit_message_text(
                    text=message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
                )
            else:
                await self.bot.send_message(
                    chat_id=user_id, text=message_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
                )
        except Exception as e:
            logger.error(f"Error in send_privacy_policy handler: {e}", exc_info=True)

    async def handle_privacy_response(self, update, context):
        query = update.callback_query
        await query.answer()
        try:
            user_id = query.from_user.id
            lang, current_question_index, responses, chat_id = self.google_sheets.get_user_state(user_id)
            if query.data == "privacy_accept":
                form = ApplicationForm(lang, self.localization)
                form.current_question_index = current_question_index
                form.responses = responses
                self.user_forms[user_id] = form
                self._save_user_state(user_id, lang, form.current_question_index, form.responses, chat_id)
                await self._send_next_question(user_id)
            else:
                await query.edit_message_text(text=self.localization.get_string(lang, "decline_message"))
        except Exception as e:
            logger.error(f"Error in handle_privacy_response handler: {e}", exc_info=True)

    async def handle_response(self, update, context):
        try:
            user_id = update.message.from_user.id
            form = self.user_forms.get(user_id)
            if not form:
                lang, current_question_index, responses, chat_id = self.google_sheets.get_user_state(user_id)
                if not lang:
                    await update.message.reply_text(self.localization.get_string("en", "error_message"))
                    return
                form = ApplicationForm(lang, self.localization)
                form.current_question_index = current_question_index
                form.responses = responses
                self.user_forms[user_id] = form
            user_response = update.message.text.strip()
            if not await self._validate_and_handle_response(user_response, form, user_id):
                return
            if form.is_complete():
                self.google_sheets.save_to_sheet(user_id, form.get_all_responses())
                del self.user_forms[user_id]
                await update.message.reply_text(self.localization.get_string(form.lang, "application_complete"))
                await self.approve_join_request(user_id, context)
            else:
                await self._send_next_question(user_id)
        except Exception as e:
            logger.error(f"Error in handle_response handler: {e}", exc_info=True)

    async def handle_join_request(self, update, context):
        try:
            join_request = update.chat_join_request
            user_id = join_request.from_user.id
            chat_id = join_request.chat.id
            self._save_user_state(user_id, "", 0, {}, str(chat_id))
            await self.start(update, context)
        except Exception as e:
            logger.error(f"Error in handle_join_request handler: {e}", exc_info=True)

    async def approve_join_request(self, user_id, context):
        try:
            _, _, _, chat_id = self.google_sheets.get_user_state(user_id)
            if not chat_id:
                return
            await context.bot.approve_chat_join_request(chat_id=int(chat_id), user_id=user_id)
            await self.utils.notify_admin(f"✅ User {user_id} has been approved.")
        except Exception as e:
            logger.error(f"Error in approve_join_request handler: {e}", exc_info=True)

    def setup(self, application):
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CallbackQueryHandler(self.set_language, pattern="^lang_"))
        application.add_handler(CallbackQueryHandler(self.handle_privacy_response, pattern="^privacy_"))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_response))
        application.add_handler(ChatJoinRequestHandler(self.handle_join_request))

    def _save_user_state(self, user_id, lang, current_question_index, responses, chat_id):
        self.google_sheets.save_user_state(user_id, lang, current_question_index, responses, chat_id)

    async def _send_next_question(self, user_id):
        form = self.user_forms.get(user_id)
        next_question = form.get_next_question() if form else None
        if next_question:
            self._save_user_state(user_id, form.lang, form.current_question_index, form.responses, self.google_sheets.get_chat_id(user_id))
            await self.bot.send_message(chat_id=user_id, text=next_question)

    async def _validate_and_handle_response(self, user_response, form, user_id):
        current_question_type = form.get_current_question_type()
        if current_question_type == "email" and not Validation.validate_email(user_response):
            await self.bot.send_message(chat_id=user_id, text=self.localization.get_string(form.lang, "invalid_email"))
            return False
        if current_question_type == "phone" and not Validation.validate_phone(user_response):
            await self.bot.send_message(chat_id=user_id, text=self.localization.get_string(form.lang, "invalid_phone"))
            return False
        if current_question_type == "age" and not Validation.validate_age(user_response):
            await self.bot.send_message(chat_id=user_id, text=self.localization.get_string(form.lang, "invalid_age"))
            return False
        form.save_response(user_response)
        return True
