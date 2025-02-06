import json
from gspread import Client, exceptions
from google.oauth2.service_account import Credentials
from shared.telegram_bot.logger import logger
from shared.telegram_bot.config import Config

CREDENTIALS = None
SHEET_CLIENT = None
MAIN_SHEET = None
METADATA_SHEET = None

def get_google_sheets_connection(force_refresh=False):
    logger.info(f"get_google_sheets_connection called with force_refresh={force_refresh}")
    global CREDENTIALS, SHEET_CLIENT, MAIN_SHEET, METADATA_SHEET
    if force_refresh or not CREDENTIALS or not SHEET_CLIENT:
        logger.info("Initializing Google Sheets Credentials/Client.")
        CREDENTIALS = Credentials.from_service_account_info(
            Config.SERVICE_ACCOUNT_INFO, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        SHEET_CLIENT = Client(auth=CREDENTIALS)
    if force_refresh or not MAIN_SHEET or not METADATA_SHEET:
        logger.info("Opening main_sheet and metadata_sheet from Google Sheets.")
        google_sheet = SHEET_CLIENT.open_by_key(Config.GOOGLE_SHEET_ID)
        MAIN_SHEET = google_sheet.sheet1
        METADATA_SHEET = google_sheet.worksheet("Metadata")
    return MAIN_SHEET, METADATA_SHEET

class GoogleSheets:
    def __init__(self):
        logger.info("Initializing GoogleSheets class instance.")
        self.main_sheet, self.metadata_sheet = get_google_sheets_connection()

    def _retry_on_failure(self, func, *args, **kwargs):
        logger.info(f"_retry_on_failure called for {func.__name__}")
        try:
            return func(*args, **kwargs)
        except exceptions.APIError as e:
            logger.error(f"Google Sheets API error: {e}, retrying with refreshed connection...", exc_info=True)
            self.main_sheet, self.metadata_sheet = get_google_sheets_connection(force_refresh=True)
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Unexpected error while accessing Google Sheets: {e}", exc_info=True)
            raise

    def save_to_sheet(self, user_id, responses):
        logger.info(f"save_to_sheet called for user_id={user_id} with responses={responses}")
        def append_row():
            column_order = ["User ID", "Full Name", "Age", "Email", "Phone", "Purpose"]
            row = [str(user_id)] + [responses.get(column, "") for column in column_order[1:]]
            self.main_sheet.append_row(row)
        self._retry_on_failure(append_row)

    def save_user_state(self, user_id: str, lang: str, current_question_index: int, responses: dict, chat_id: str,
                        last_question=None):
        def save_state():
            responses_json = json.dumps(responses)
            new_row = [str(user_id), str(chat_id), lang, str(current_question_index), responses_json,
                       last_question or ""]
            records = self.metadata_sheet.get_all_records()
            for i, record in enumerate(records):
                if str(record.get('User ID', '')) == str(user_id):
                    self.metadata_sheet.update(f"A{i + 2}:F{i + 2}", [new_row])
                    return
            self.metadata_sheet.append_row(new_row)
        self._retry_on_failure(save_state)

    def get_user_state(self, user_id):
        logger.info(f"get_user_state called for user_id={user_id}")
        def fetch_state():
            records = self.metadata_sheet.get_all_records()
            for record in records:
                if str(record['User ID']) == str(user_id):
                    responses = json.loads(record['Responses']) if record['Responses'] else []
                    if isinstance(responses, dict):
                        responses = [(k, v) for k, v in responses.items()]
                    return (
                        record['Language'],
                        int(record['Current Question Index']),
                        responses,
                        record.get('Chat ID', "")
                    )
            return None, 0, [], ""
        return self._retry_on_failure(fetch_state)

    def get_chat_id(self, user_id):
        logger.info(f"get_chat_id called for user_id={user_id}")
        def fetch_chat_id():
            records = self.metadata_sheet.get_all_records()
            for record in records:
                if str(record['User ID']) == str(user_id):
                    return record.get('Chat ID', "")
            return ""
        return self._retry_on_failure(fetch_chat_id)
