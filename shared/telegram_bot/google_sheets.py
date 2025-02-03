import os
import gspread
from google.oauth2.service_account import Credentials


class GoogleSheets:
    """
    Class to manage Google Sheets interactions and save user responses.
    """

    def __init__(self):
        """
        Initializes the Google Sheets client using environment variables for the service account.
        """
        # Collect service account information from environment variables.
        service_account_info = {
            "type": os.getenv("TEST_SERVICE_ACCOUNT_TYPE"),
            "project_id": os.getenv("TEST_SERVICE_ACCOUNT_PROJECT_ID"),
            "private_key_id": os.getenv("TEST_SERVICE_ACCOUNT_PRIVATE_KEY_ID"),
            "private_key": os.getenv("TEST_SERVICE_ACCOUNT_PRIVATE_KEY").replace("\\n", "\n"),
            "client_email": os.getenv("TEST_SERVICE_ACCOUNT_CLIENT_EMAIL"),
            "client_id": os.getenv("TEST_SERVICE_ACCOUNT_CLIENT_ID"),
            "auth_uri": os.getenv("TEST_SERVICE_ACCOUNT_AUTH_URI"),
            "token_uri": os.getenv("TEST_SERVICE_ACCOUNT_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("TEST_SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("TEST_SERVICE_ACCOUNT_CLIENT_CERT_URL"),
        }

        # Validate that the service account info has all required fields.
        GoogleSheets._validate_service_account_info(service_account_info)

        # Get Google Sheet ID from environment variable and ensure it's provided.
        sheet_id = os.getenv("TEST_GOOGLE_SHEET_ID")
        if not sheet_id:
            raise EnvironmentError("TEST_GOOGLE_SHEET_ID environment variable is not set.")

        # Authenticate with the Google Sheets API using the service account credentials.
        credentials = Credentials.from_service_account_info(service_account_info)
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open_by_key(sheet_id).sheet1  # Open the first sheet.

    def save_to_sheet(self, user_id, responses):
        """
        Saves user responses to Google Sheets.

        :param user_id: Telegram user ID as a string.
        :param responses: Dictionary of user responses with questions as keys and answers as values.
        """
        try:
            # Prepare the row to append: first column is the user ID, followed by their responses.
            row = [str(user_id)] + list(responses.values())

            # Append the row to the sheet.
            self.sheet.append_row(row)
        except Exception as e:
            # Log any errors that occur during the process of saving responses.
            print(f"Error saving to Google Sheets: {e}")

    @staticmethod
    def _validate_service_account_info(service_account_info):
        """
        Validates that all required fields for the service account are present.

        :param service_account_info: Dictionary containing service account information.
        :raises ValueError: If any required field is missing.
        """
        # List of required fields needed for successful authentication.
        required_keys = [
            "type", "project_id", "private_key_id", "private_key", "client_email",
            "client_id", "auth_uri", "token_uri",
            "auth_provider_x509_cert_url", "client_x509_cert_url"
        ]

        # Check each required field to ensure it's present and not empty.
        for key in required_keys:
            if not service_account_info.get(key):
                raise ValueError(f"Missing required service account field: {key}.")
