import os

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_BOT_TOKEN:
        raise EnvironmentError("TELEGRAM_BOT_TOKEN environment variable is not set.")
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
    if not ADMIN_CHAT_ID:
        raise EnvironmentError("ADMIN_CHAT_ID environment variable is not set.")
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
    if not GOOGLE_SHEET_ID:
        raise EnvironmentError("GOOGLE_SHEET_ID environment variable is not set.")
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
    PRIVACY_POLICY_URLS = {
        "ru": os.getenv("PRIVACY_POLICY_URL_RU"),
        "kz": os.getenv("PRIVACY_POLICY_URL_KZ"),
        "en": os.getenv("PRIVACY_POLICY_URL_EN"),
    }

    @staticmethod
    def get_privacy_policy_url(lang):
        return Config.PRIVACY_POLICY_URLS.get(lang, Config.PRIVACY_POLICY_URLS["en"])
