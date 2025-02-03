import os
import gspread
from google.oauth2.service_account import Credentials

class GoogleSheets:
    """
    Class to manage Google Sheets interactions.
    """

    def __init__(self):
        """
        Initializes the Google Sheets client using environment variables.
        Ensures the correct format of the service account's private key.
        """
        # Load service account credentials from environment variables.
        service_account_info = {
            "type": os.getenv("SERVICE_ACCOUNT_TYPE"),
            "project_id": os.getenv("SERVICE_ACCOUNT_PROJECT_ID"),
            "private_key_id": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY_ID"),
            # Correctly handle the private key by converting escaped \n to actual newlines
            "private_key": self._get_private_key(),
            "client_email": os.getenv("SERVICE_ACCOUNT_CLIENT_EMAIL"),
            "client_id": os.getenv("SERVICE_ACCOUNT_CLIENT_ID"),
            "auth_uri": os.getenv("SERVICE_ACCOUNT_AUTH_URI"),
            "token_uri": os.getenv("SERVICE_ACCOUNT_TOKEN_URI"),
            "auth_provider_x509_cert_url": os.getenv("SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL"),
            "client_x509_cert_url": os.getenv("SERVICE_ACCOUNT_CLIENT_CERT_URL"),
        }

        # Validate service account information
        self._validate_service_account_info(service_account_info)

        # Fetch Google Sheet ID from environment variables
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            raise EnvironmentError("GOOGLE_SHEET_ID environment variable is not set.")

        # Authorize Google Sheets API
        credentials = Credentials.from_service_account_info(service_account_info)
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    @staticmethod
    def _get_private_key():
        """
        Retrieves and processes the service account's private key.
        Ensures that the key is correctly formatted with newlines.

        :return: The properly formatted private key.
        """
        private_key = os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY", "").replace("\\n", "\n")
        if not private_key.startswith("-----BEGIN PRIVATE KEY-----"):
            raise ValueError("Invalid private key format. Please check the SERVICE_ACCOUNT_PRIVATE_KEY environment variable.")
        return private_key

    @staticmethod
    def _validate_service_account_info(service_account_info):
        """
        Validates that all required fields in the service account information are set.

        :param service_account_info: Dictionary containing the service account fields.
        :raises EnvironmentError: If any required field is missing or empty.
        """
        for key, value in service_account_info.items():
            if not value:
                raise EnvironmentError(f"Missing or empty service account field: {key}")

    def save_to_sheet(self, user_id, responses):
        """
        Saves user responses to Google Sheets.

        :param user_id: Telegram user ID as a string.
        :param responses: Dictionary of user responses.
        """
        try:
            # Prepare the row to append: user_id followed by all responses
            row = [str(user_id)] + list(responses.values())
            # Append the row to the sheet
            self.sheet.append_row(row)
        except Exception as e:
            print(f"Error saving to Google Sheets: {e}")
