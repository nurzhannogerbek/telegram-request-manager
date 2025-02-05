import os
import json
import gspread
import logging
from google.oauth2.service_account import Credentials

# Configure logging to track Google Sheets interactions and errors.
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GoogleSheets:
    """
    Class to manage Google Sheets interactions and save user responses.
    """

    def __init__(self):
        """
        Initializes the Google Sheets client using environment variables for the service account credentials.
        Includes debug logging to verify the correct loading of environment variables.
        """
        # Collect service account information from environment variables.
        service_account_info = {
            "type": os.getenv("SERVICE_ACCOUNT_TYPE"),
            "project_id": os.getenv("SERVICE_ACCOUNT_PROJECT_ID"),
            "private_key_id": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY_ID"),
            "private_key": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("SERVICE_ACCOUNT_CLIENT_EMAIL"),
            "client_id": os.getenv("SERVICE_ACCOUNT_CLIENT_ID"),
            "auth_uri": os.getenv("SERVICE_ACCOUNT_AUTH_URI"),
            "token_uri": os.getenv("SERVICE_ACCOUNT_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("SERVICE_ACCOUNT_CLIENT_CERT_URL"),
        }

        # Debug: Log the first 10 characters of sensitive environment variables to ensure correct loading.
        print(f"Debug: SERVICE_ACCOUNT_PRIVATE_KEY starts with: {service_account_info['private_key'][:10]}...")
        print(f"Debug: SERVICE_ACCOUNT_CLIENT_EMAIL: {service_account_info['client_email'][:5]}...")
        print(f"Debug: SERVICE_ACCOUNT_PROJECT_ID: {service_account_info['project_id']}")

        # Specify required scopes for Google Sheets API.
        scopes = ["https://www.googleapis.com/auth/spreadsheets"]

        # Authenticate using the service account credentials and required scopes.
        credentials = Credentials.from_service_account_info(service_account_info, scopes=scopes)
        self.client = gspread.authorize(credentials)

        # Retrieve the Google Sheet.
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            logger.error("Environment variable GOOGLE_SHEET_ID is not set.")
            raise EnvironmentError("GOOGLE_SHEET_ID environment variable is not set.")
        self.sheet = self.client.open_by_key(sheet_id).sheet1

        # Log successful connection.
        print("Successfully connected to Google Sheets.")

    def save_to_sheet(self, user_id, responses):
        """
        Saves user responses to the "Telegram Users" sheet.

        :param user_id: Telegram user ID as a string.
        :param responses: Dictionary of user responses with questions as keys and answers as values.
        """
        try:
            # Define the column order based on the sheet headers.
            column_order = ["User ID", "Full Name", "Age", "Email", "Phone", "Purpose"]

            # Map responses to the correct column order.
            row = [str(user_id)]  # The first column is always the user ID.

            # Fill the row with answers based on the order of the columns.
            for column in column_order[1:]:
                # Match the question text with the response in the dictionary.
                response = responses.get(column, "")  # Return an empty string if no response is found.
                row.append(response)

            # Append the row to the "Telegram Users" sheet.
            self.sheet.append_row(row)

        except Exception as e:
            print(f"Error saving to Google Sheets for user {user_id}: {e}.")

    @staticmethod
    def _validate_service_account_info(service_account_info):
        """
        Validates that the service account information contains all required fields.

        :param service_account_info: Dictionary containing service account information.
        :raises ValueError: If any required field is missing.
        """
        required_keys = [
            "type", "project_id", "private_key_id", "private_key", "client_email",
            "client_id", "auth_uri", "token_uri",
            "auth_provider_x509_cert_url", "client_x509_cert_url"
        ]

        # Check that each required key is present and non-empty.
        for key in required_keys:
            if not service_account_info.get(key):
                # Log the missing field.
                logger.error(f"Missing required service account field: {key}.")
                raise ValueError(f"Missing required service account field: {key}.")
        # Log successful validation.
        print("Service account credentials validated successfully.")

    def save_user_state(self, user_id: str, lang: str, current_question_index: int, responses: dict, chat_id: str = ""):
        """
        Saves the user's current state (language, question index, responses, and chat_id) to the Metadata sheet.
        """
        try:
            # Access the Metadata worksheet in the Google Sheet.
            user_states_sheet = self.client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet("Metadata")

            # Convert responses to a JSON string to store in the sheet.
            responses_json = json.dumps(responses)

            # Prepare the row to store user state.
            new_row = [str(user_id), lang or "", str(current_question_index), responses_json, str(chat_id or "")]

            # Retrieve existing records.
            records = user_states_sheet.get_all_records()

            # Check if the user already exists in the records.
            for i, record in enumerate(records):
                if str(record.get('User ID', '')) == str(user_id):
                    # Update the user's state in the corresponding row.
                    user_states_sheet.update(f"A{i + 2}:E{i + 2}", [[str(x) for x in new_row]])  # type: ignore
                    print(f"Updated state for user {user_id}.")
                    return

            # Append the new row if the user does not exist.
            user_states_sheet.append_row([str(x) for x in new_row])
            print(f"Saved new state for user {user_id}.")

        except Exception as e:
            print(f"Error saving user state for {user_id}: {e}")

    def get_user_state(self, user_id):
        """
        Retrieves the saved state (language, question index, responses, and chat_id) for a given user.

        :param user_id: The unique Telegram user ID.
        :return: A tuple containing (lang, current_question_index, responses, chat_id).
        """
        try:
            # Access the Metadata worksheet in the Google Sheet.
            user_states_sheet = self.client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet("Metadata")

            # Retrieve all current rows from the sheet.
            records = user_states_sheet.get_all_records()

            # Search for the user ID in the rows.
            for record in records:
                if str(record['User ID']) == str(user_id):
                    # Extract and return the saved state.
                    lang = record['Language']
                    current_question_index = int(record['Current Question Index'])
                    responses = json.loads(record['Responses']) if record['Responses'] else {}
                    chat_id = record.get('Chat ID', None)
                    return lang, current_question_index, responses, chat_id

        except Exception as e:
            print(f"Error retrieving user state for {user_id}: {e}")

        # Return default state if the user is not found.
        return None, 0, {}, None

    def get_chat_id(self, user_id):
        """
        Retrieves the saved chat ID for a given user from the Metadata sheet.

        :param user_id: The unique Telegram user ID.
        :return: The chat ID as a string or an empty string if not found.
        """
        try:
            user_states_sheet = self.client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).worksheet("Metadata")
            records = user_states_sheet.get_all_records()

            for record in records:
                if str(record['User ID']) == str(user_id):
                    return record.get('Chat ID', "")
        except Exception as e:
            print(f"Error retrieving chat ID for user {user_id}: {e}")
        return ""

