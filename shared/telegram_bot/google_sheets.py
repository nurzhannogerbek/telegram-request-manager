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
            "type": os.getenv("SERVICE_ACCOUNT_TYPE"),  # The type of service account (e.g., 'service_account').
            "project_id": os.getenv("SERVICE_ACCOUNT_PROJECT_ID"),  # The project ID of the service account.
            "private_key_id": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY_ID"),  # The private key ID for authentication.
            "private_key": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY").replace("\\n", "\n"),  # The private key, formatted correctly.
            "client_email": os.getenv("SERVICE_ACCOUNT_CLIENT_EMAIL"),  # The client email for the service account.
            "client_id": os.getenv("SERVICE_ACCOUNT_CLIENT_ID"),  # The client ID associated with the service account.
            "auth_uri": os.getenv("SERVICE_ACCOUNT_AUTH_URI"),  # OAuth2 authentication URI.
            "token_uri": os.getenv("SERVICE_ACCOUNT_TOKEN_URI"),  # The URI for obtaining OAuth2 tokens.
            "auth_provider_x509_cert_url": os.getenv("SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL"),  # URL for provider certificates.
            "client_x509_cert_url": os.getenv("SERVICE_ACCOUNT_CLIENT_CERT_URL")  # URL for client certificates.
        }

        # Validate that the service account information contains all required fields.
        self._validate_service_account_info(service_account_info)

        # Retrieve the Google Sheet ID from environment variables.
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            logger.error("Environment variable GOOGLE_SHEET_ID is not set.")
            raise EnvironmentError("GOOGLE_SHEET_ID environment variable is not set.")

        logger.info("Authenticating with Google Sheets API.")  # Log the start of the authentication process.

        # Authenticate with Google Sheets using the service account credentials.
        credentials = Credentials.from_service_account_info(service_account_info)

        # Authorize the gspread client with the authenticated credentials.
        self.client = gspread.authorize(credentials)

        # Open the first sheet in the specified Google Sheet by its ID.
        self.sheet = self.client.open_by_key(sheet_id).sheet1

        logger.info("Successfully connected to Google Sheets.")  # Log successful connection to the Google Sheet.

    def save_to_sheet(self, user_id, responses):
        """
        Saves user responses to Google Sheets.

        :param user_id: Telegram user ID as a string.
        :param responses: Dictionary of user responses with questions as keys and answers as values.
        """
        try:
            # Prepare the row to be inserted into the Google Sheet: user ID followed by all response values.
            row = [str(user_id)] + list(responses.values())
            logger.info(f"Saving responses to Google Sheets for user {user_id}: {responses}.")  # Log the saving action.

            # Append the row to the Google Sheet as a new entry.
            self.sheet.append_row(row)
            logger.info(f"Successfully saved responses for user {user_id}.")  # Log successful saving of the responses.

        except Exception as e:
            logger.error(f"Error saving to Google Sheets for user {user_id}: {e}.")  # Log the error if saving fails.
            raise  # Re-raise the exception to handle it in the calling function.

    @staticmethod
    def _validate_service_account_info(service_account_info):
        """
        Validates that the service account information contains all required fields.

        :param service_account_info: Dictionary containing service account information.
        :raises ValueError: If any required field is missing.
        """
        # Define the list of required fields for the service account.
        required_keys = [
            "type", "project_id", "private_key_id", "private_key", "client_email",
            "client_id", "auth_uri", "token_uri",
            "auth_provider_x509_cert_url", "client_x509_cert_url"
        ]

        # Check that each required key is present and not empty.
        for key in required_keys:
            if not service_account_info.get(key):
                # Log the missing field.
                logger.error(f"Missing required service account field: {key}.")
                # Raise an error if a field is missing.
                raise ValueError(f"Missing required service account field: {key}.")
        # Log successful validation.
        logger.info("Service account credentials validated successfully.")
