import json
from gspread import Client, exceptions
from google.oauth2.service_account import Credentials
from shared.telegram_bot.logger import logger
from shared.telegram_bot.config import Config

# Global variables for managing Google Sheets connections and worksheets.
CREDENTIALS = None  # Stores the Google service account credentials.
SHEET_CLIENT = None  # Stores the Google Sheets client instance.
MAIN_SHEET = None  # Reference to the main Google Sheets worksheet.
METADATA_SHEET = None  # Reference to the metadata worksheet.


def get_google_sheets_connection(force_refresh=False):
    """
    Establishes or retrieves the connection to Google Sheets, refreshing it if necessary.

    Args:
        force_refresh (bool): If True, forces the reinitialization of credentials and connections.

    Returns:
        tuple: A tuple containing references to the main and metadata sheets.
    """
    global CREDENTIALS, SHEET_CLIENT, MAIN_SHEET, METADATA_SHEET

    # Reinitialize credentials and client if force_refresh is requested or no existing connection is found.
    if force_refresh or not CREDENTIALS or not SHEET_CLIENT:
        # Load the service account credentials from environment variables.
        CREDENTIALS = Credentials.from_service_account_info(
            Config.SERVICE_ACCOUNT_INFO, scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        # Create a Google Sheets client using the credentials.
        SHEET_CLIENT = Client(auth=CREDENTIALS)

    # Open and access the main and metadata sheets if needed.
    if force_refresh or not MAIN_SHEET or not METADATA_SHEET:
        # Open the Google Sheets document using its unique ID.
        google_sheet = SHEET_CLIENT.open_by_key(Config.GOOGLE_SHEET_ID)
        # Access the first sheet (typically used for main data storage).
        MAIN_SHEET = google_sheet.sheet1
        # Access the metadata worksheet where user states are saved.
        METADATA_SHEET = google_sheet.worksheet("Metadata")

    return MAIN_SHEET, METADATA_SHEET


class GoogleSheets:
    """
    Provides methods for interacting with Google Sheets to store user responses and manage state.
    Handles retry mechanisms to recover from API errors and ensures robust interaction.
    """

    def __init__(self):
        """
        Initializes the GoogleSheets instance and establishes connections to the necessary worksheets.
        """
        # Establish connection to main and metadata sheets during initialization.
        self.main_sheet, self.metadata_sheet = get_google_sheets_connection()

    def _retry_on_failure(self, func, *args, **kwargs):
        """
        Executes the given function and retries with refreshed connections if an API error occurs.

        Args:
            func (callable): The function to execute.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            Any: The result of the function call.

        Raises:
            Exception: If an unexpected error occurs after retries.
        """
        try:
            return func(*args, **kwargs)
        except exceptions.APIError as e:
            # Log the API error and attempt to refresh the connection.
            logger.error(f"Google Sheets API error: {e}, retrying with refreshed connection...", exc_info=True)
            self.main_sheet, self.metadata_sheet = get_google_sheets_connection(force_refresh=True)
            return func(*args, **kwargs)
        except Exception as e:
            # Log any unexpected error and re-raise it.
            logger.error(f"Unexpected error while accessing Google Sheets: {e}", exc_info=True)
            raise

    def save_to_sheet(self, user_id, responses):
        """
        Saves the user's responses to the main Google Sheets worksheet.

        Args:
            user_id (str): The unique identifier of the user.
            responses (dict): The user's responses mapped by field names.
        """

        def append_row():
            # Define the order of columns where responses will be stored.
            column_order = [
                "User ID",
                "Full Name",
                "Age",
                "Email",
                "Phone",
                "Purpose",
                "Occupation",
                "Workplace",
                "City",
                "Username",
                "Bio"
            ]
            # Create a new row with the user's ID and their responses, ensuring fields match the column order.
            row = [str(user_id)] + [responses.get(column, "") for column in column_order[1:]]
            # Append the row to the main sheet.
            self.main_sheet.append_row(row)

        # Retry the append operation in case of transient failures.
        self._retry_on_failure(append_row)

    def save_user_state(self, user_id, lang, current_question_index, responses, chat_id=None, last_question=None):
        """
        Saves the user's current state, including responses and progress, to the metadata worksheet.

        Args:
            user_id (str): The unique identifier of the user.
            lang (str): The selected language of the user.
            current_question_index (int): The index of the current question being asked.
            responses (dict): The user's responses.
            chat_id (str, optional): The group chat ID where the user wants to join.
            last_question (str, optional): The last question asked (if applicable).
        """

        def save_state():
            # Ensure chat_id is a **valid string** and not None.
            local_chat_id = str(chat_id) if chat_id else ""  # Renamed to `local_chat_id` to avoid reference issues.

            # Ensure that chat_id is the **group chat ID**, not a personal chat ID.
            if not local_chat_id.startswith("-"):
                local_chat_id = ""  # If it's not a group ID, we clear it to avoid issues.

            # Serialize the user's responses into a JSON string for storage.
            responses_json = json.dumps(responses)

            # Prepare the row with user state information.
            new_row = [str(user_id), local_chat_id, lang, str(current_question_index), responses_json, last_question or ""]
            records = self.metadata_sheet.get_all_records()

            # Check if the user already exists in the metadata sheet.
            for i, record in enumerate(records):
                if str(record.get('User ID', '')) == str(user_id):
                    # Update the existing row with the new state.
                    self.metadata_sheet.update(f"A{i + 2}:F{i + 2}", [new_row])
                    return

            # Append a new row if the user is not found.
            self.metadata_sheet.append_row(new_row)

        # Retry the state-saving operation if necessary.
        self._retry_on_failure(save_state)

    def get_user_state(self, user_id):
        """
        Retrieves the user's saved state from the metadata worksheet.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            tuple: A tuple containing language, current question index, responses, and chat ID.
        """

        def fetch_state():
            # Retrieve all records from the metadata sheet.
            records = self.metadata_sheet.get_all_records()
            for record in records:
                if str(record['User ID']) == str(user_id):
                    # Deserialize the saved responses from JSON.
                    responses = json.loads(record['Responses']) if record['Responses'] else []
                    # Ensure responses are formatted as a list of tuples if necessary.
                    if isinstance(responses, dict):
                        responses = [(k, v) for k, v in responses.items()]
                    return (
                        record['Language'],
                        int(record['Current Question Index']),
                        responses,
                        record.get('Chat ID', "")
                    )
            # Return default values if no state is found for the user.
            return None, 0, [], ""

        # Retry the state-fetching operation if necessary.
        return self._retry_on_failure(fetch_state)

    def get_chat_id(self, user_id):
        """
        Retrieves the user's Telegram chat ID from the metadata worksheet.

        Args:
            user_id (str): The unique identifier of the user.

        Returns:
            str: The user's chat ID, or an empty string if not found.
        """

        def fetch_chat_id():
            # Retrieve all records from the metadata sheet.
            records = self.metadata_sheet.get_all_records()
            for record in records:
                if str(record['User ID']) == str(user_id):
                    # Return the associated chat ID if found.
                    return record.get('Chat ID', "")
            # Return an empty string if no chat ID is found.
            return ""

        # Retry the chat ID-fetching operation if necessary.
        return self._retry_on_failure(fetch_chat_id)
