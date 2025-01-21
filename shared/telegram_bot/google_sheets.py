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
        """
        # Load service account credentials from environment variables.
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

        # Fetch Google Sheet ID from environment variables.
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            raise EnvironmentError("GOOGLE_SHEET_ID environment variable is not set.")

        # Authorize Google Sheets API.
        credentials = Credentials.from_service_account_info(service_account_info)
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open_by_key(sheet_id).sheet1

    def save_to_sheet(self, user_id, responses):
        """
        Saves user responses to Google Sheets.

        :param user_id: Telegram user ID as a string.
        :param responses: Dictionary of user responses.
        """
        try:
            row = [str(user_id)] + list(responses.values())
            self.sheet.append_row(row)
        except Exception as e:
            print(f"Error saving to Google Sheets: {e}")
