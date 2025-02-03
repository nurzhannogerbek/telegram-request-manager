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

        # Validate that the service account information contains all required fields.
        self._validate_service_account_info(service_account_info)

        # Retrieve the Google Sheet ID from environment variables.
        sheet_id = os.getenv("TEST_GOOGLE_SHEET_ID")
        if not sheet_id:
            logger.error("Environment variable TEST_GOOGLE_SHEET_ID is not set.")
            raise EnvironmentError("TEST_GOOGLE_SHEET_ID environment variable is not set.")

        logger.info("Authenticating with Google Sheets API.")  # Log authentication status.

        # Authenticate with Google Sheets using the service account credentials.
        credentials = Credentials.from_service_account_info(service_account_info)
        self.client = gspread.authorize(credentials)
        self.sheet = self.client.open_by_key(sheet_id).sheet1  # Open the first sheet in the spreadsheet.

        logger.info("Successfully connected to Google Sheets.")  # Log successful connection.

    def save_to_sheet(self, user_id, responses):
        """
        Saves user responses to Google Sheets.

        :param user_id: Telegram user ID as a string.
        :param responses: Dictionary of user responses with questions as keys and answers as values.
        """
        try:
            # Prepare the row: user ID followed by all response values.
            row = [str(user_id)] + list(responses.values())
            logger.info(f"Saving responses to Google Sheets for user {user_id}: {responses}.")  # Log saving action.

            # Append the row to the Google Sheet.
            self.sheet.append_row(row)
            logger.info(f"Successfully saved responses for user {user_id}.")  # Log success.

        except Exception as e:
            logger.error(f"Error saving to Google Sheets for user {user_id}: {e}.")  # Log any errors.
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
                logger.error(f"Missing required service account field: {key}.")  # Log the missing field.
                raise ValueError(f"Missing required service account field: {key}.")

        logger.info("Service account credentials validated successfully.")  # Log successful validation.
