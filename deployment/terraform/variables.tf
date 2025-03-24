# Variable to specify the Telegram Bot Token for authentication.
variable "telegram_bot_token" {
  description = "Telegram Bot Token to authenticate the bot with Telegram API."
}

# Variable to specify the Telegram Admin Chat ID for sending updates.
variable "admin_chat_id" {
  description = "Telegram Admin Chat ID where notifications or updates will be sent."
}

# Variable to specify the Google Sheet ID used to store bot responses.
variable "google_sheet_id" {
  description = "Google Sheet ID where responses from the Telegram bot will be logged."
}

# Variable specifying the type of service account (typically 'service_account').
variable "service_account_type" {
  description = "Service account type required for Google API authentication."
}

# Project ID associated with the service account for Google API access.
variable "service_account_project_id" {
  description = "The project ID associated with the Google service account."
}

# ID of the private key associated with the service account.
variable "service_account_private_key_id" {
  description = "The private key ID associated with the Google service account."
}

# The private key of the service account for secure authentication.
variable "service_account_private_key" {
  description = "The private key associated with the Google service account, used for authentication."
}

# Client email for the service account to access Google APIs.
variable "service_account_client_email" {
  description = "The email address of the Google service account."
}

# Client ID of the service account.
variable "service_account_client_id" {
  description = "The client ID of the Google service account."
}

# OAuth 2.0 authentication URI for the Google service account.
variable "service_account_auth_uri" {
  description = "The URI for OAuth 2.0 authentication for the Google service account."
}

# URI for retrieving OAuth 2.0 tokens.
variable "service_account_token_uri" {
  description = "The URI used to retrieve OAuth 2.0 tokens for the Google service account."
}

# URL providing access to Google API provider certificates.
variable "service_account_auth_provider_cert_url" {
  description = "URL for Google’s OAuth provider certificates."
}

# URL to retrieve service account metadata, including client certificates.
variable "service_account_client_cert_url" {
  description = "URL that points to the service account's client certificates for API access."
}

# Name of the project in Terraform configuration.
variable "project_name" {
  description = "The project name used to create unique resource identifiers."
}

# Environment name (e.g., test, prod).
variable "environment" {
  description = "The environment where the resources will be deployed (e.g., test or production)."
}

# API Gateway stage name (e.g., test, prod).
variable "api_stage_name" {
  description = "The stage name for the API Gateway (test or production)."
}

# AWS region where the infrastructure is deployed.
variable "aws_region" {
  description = "AWS region where the infrastructure is deployed."
}

# Variable for the URL of the Russian privacy policy.
variable "privacy_policy_url_ru" {
  description = "URL for the Russian privacy policy."
}

# Variable for the URL of the English privacy policy.
variable "privacy_policy_url_en" {
  description = "URL for the English privacy policy."
}

# Variable for the URL of the Kazakh privacy policy.
variable "privacy_policy_url_kz" {
  description = "URL for the Kazakh privacy policy."
}

# Variable for the Telegram group invite link.
variable "group_invite_link" {
  description = "Telegram group invite link that will be sent to users after completing the questionnaire."
}