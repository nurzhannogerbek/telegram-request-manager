# Environment-specific variables for the test environment.
project_name = "telegram-request-manager"
environment  = "test"
api_stage_name = "test"

telegram_bot_token = var.telegram_bot_token
admin_chat_id = var.admin_chat_id
google_sheet_id = var.google_sheet_id

service_account_type = var.service_account_type
service_account_project_id = var.service_account_project_id
service_account_private_key_id = var.service_account_private_key_id
service_account_private_key = var.service_account_private_key
service_account_client_email = var.service_account_client_email
service_account_client_id = var.service_account_client_id
service_account_auth_uri = var.service_account_auth_uri
service_account_token_uri = var.service_account_token_uri
service_account_auth_provider_cert_url = var.service_account_auth_provider_cert_url
service_account_client_cert_url = var.service_account_client_cert_url
