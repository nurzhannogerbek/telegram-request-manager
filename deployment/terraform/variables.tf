# Environment-specific variables.
variable "environment" {
  description = "Environment name (e.g., dev, prod)."
}

variable "lambda_function_name" {
  description = "Base name for the Lambda function."
}

variable "api_gateway_name" {
  description = "Base name for the API Gateway."
}

variable "api_stage_name" {
  description = "Stage name for the API Gateway."
}

# Sensitive data variables.
variable "telegram_bot_token" {
  description = "Telegram bot token."
}

variable "admin_chat_id" {
  description = "Admin chat ID for Telegram notifications."
}

variable "google_sheet_id" {
  description = "Google Sheet ID for storing user responses."
}

# Google Service Account credentials.
variable "service_account_type" {
  description = "Type of Google Service Account."
}

variable "service_account_project_id" {
  description = "Google Service Account project ID."
}

variable "service_account_private_key_id" {
  description = "Google Service Account private key ID."
}

variable "service_account_private_key" {
  description = "Google Service Account private key."
}

variable "service_account_client_email" {
  description = "Google Service Account client email."
}

variable "service_account_client_id" {
  description = "Google Service Account client ID."
}

variable "service_account_auth_uri" {
  description = "Google OAuth2 Auth URI."
}

variable "service_account_token_uri" {
  description = "Google OAuth2 Token URI."
}

variable "service_account_auth_provider_cert_url" {
  description = "Google Auth Provider Cert URL."
}

variable "service_account_client_cert_url" {
  description = "Google Client Cert URL."
}
