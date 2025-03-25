import os

class Config:
    """
    Configuration class for managing environment variables and other configuration settings.
    This class retrieves critical values such as API tokens, admin chat IDs, and Google Sheets information.
    If any required variable is missing, an error is raised to prevent misconfiguration.
    """

    # Telegram group invite link, injected via environment variables.
    GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK")
    if not GROUP_INVITE_LINK:
        raise EnvironmentError("GROUP_INVITE_LINK environment variable is not set.")

    # Retrieve the Telegram bot token from the environment variables.
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")

    # Retrieve the admin chat ID for sending critical notifications.
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
    if not ADMIN_CHAT_ID:
        raise EnvironmentError("ADMIN_CHAT_ID environment variable is not set.")

    # Default group chat ID, used as fallback if user-specific chat_id not found.
    DEFAULT_GROUP_CHAT_ID = os.getenv("DEFAULT_GROUP_CHAT_ID")
    if not DEFAULT_GROUP_CHAT_ID:
        raise EnvironmentError("DEFAULT_GROUP_CHAT_ID environment variable is not set.")

    # Retrieve the Google Sheets document ID to store user responses and metadata.
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    if not GOOGLE_SHEET_ID:
        raise EnvironmentError("GOOGLE_SHEET_ID environment variable is not set.")

    # Retrieve Google service account credentials from environment variables to authenticate with Google APIs.
    SERVICE_ACCOUNT_INFO = {
        "type": os.getenv("SERVICE_ACCOUNT_TYPE"),
        "project_id": os.getenv("SERVICE_ACCOUNT_PROJECT_ID"),
        "private_key_id": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY_ID"),
        "private_key": os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY").replace("\\n", "\n") if os.getenv("SERVICE_ACCOUNT_PRIVATE_KEY") else None,
        "client_email": os.getenv("SERVICE_ACCOUNT_CLIENT_EMAIL"),
        "client_id": os.getenv("SERVICE_ACCOUNT_CLIENT_ID"),
        "auth_uri": os.getenv("SERVICE_ACCOUNT_AUTH_URI"),
        "token_uri": os.getenv("SERVICE_ACCOUNT_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv("SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL"),
        "client_x509_cert_url": os.getenv("SERVICE_ACCOUNT_CLIENT_CERT_URL"),
    }

    # Retrieve URLs for the privacy policy in different languages.
    PRIVACY_POLICY_URLS = {
        "ru": os.getenv("PRIVACY_POLICY_URL_RU"),
        "kz": os.getenv("PRIVACY_POLICY_URL_KZ"),
        "en": os.getenv("PRIVACY_POLICY_URL_EN"),
    }

    @staticmethod
    def get_privacy_policy_url(lang):
        """
        Retrieves the privacy policy URL for the specified language.
        If the specified language is not found, the default English URL is returned.

        Args:
            lang (str): The language code (e.g., 'ru', 'kz', 'en').

        Returns:
            str: The URL of the privacy policy corresponding to the specified language.
        """
        return Config.PRIVACY_POLICY_URLS.get(lang, Config.PRIVACY_POLICY_URLS["en"])
