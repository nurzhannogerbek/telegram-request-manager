import os
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
        Saves user responses to Google Sheets.

        :param user_id: Telegram user ID as a string.
        :param responses: Dictionary of user responses with questions as keys and answers as values.
        """
        try:
            # Prepare the row: user ID followed by all response values.
            row = [str(user_id)] + list(responses.values())
            # Log saving action.
            print(f"Saving responses to Google Sheets for user {user_id}: {responses}.")

            # Append the row to the Google Sheet.
            self.sheet.append_row(row)
            # Log success.
            print(f"Successfully saved responses for user {user_id}.")

        except Exception as e:
            # Log any errors.
            logger.error(f"Error saving to Google Sheets for user {user_id}: {e}.")
            raise

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
