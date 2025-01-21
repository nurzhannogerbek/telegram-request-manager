provider "aws" {
  region = "us-east-1" # Specify your AWS region.
}

# IAM Role for Lambda.
resource "aws_iam_role" "lambda_role" {
  name = "${var.environment}_telegram_bot_lambda_role" # Include environment in the name.

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach policies to the IAM Role.
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Define the Lambda function.
resource "aws_lambda_function" "telegram_bot" {
  function_name = "${var.environment}_telegram_bot_function" # Include environment in the name.
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.9"
  filename      = "${path.module}/telegram_bot.zip" # Path to the deployment package.

  # Environment variables for Lambda.
  environment {
    variables = {
      TELEGRAM_BOT_TOKEN        = var.telegram_bot_token
      ADMIN_CHAT_ID             = var.admin_chat_id
      GOOGLE_SHEET_ID           = var.google_sheet_id
      SERVICE_ACCOUNT_TYPE      = var.service_account_type
      SERVICE_ACCOUNT_PROJECT_ID = var.service_account_project_id
      SERVICE_ACCOUNT_PRIVATE_KEY_ID = var.service_account_private_key_id
      SERVICE_ACCOUNT_PRIVATE_KEY = var.service_account_private_key
      SERVICE_ACCOUNT_CLIENT_EMAIL = var.service_account_client_email
      SERVICE_ACCOUNT_CLIENT_ID = var.service_account_client_id
      SERVICE_ACCOUNT_AUTH_URI  = var.service_account_auth_uri
      SERVICE_ACCOUNT_TOKEN_URI = var.service_account_token_uri
      SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL = var.service_account_auth_provider_cert_url
      SERVICE_ACCOUNT_CLIENT_CERT_URL = var.service_account_client_cert_url
    }
  }
}

# API Gateway setup.
resource "aws_api_gateway_rest_api" "telegram_bot_api" {
  name = "${var.environment}_telegram_bot_api" # Include environment in the name.
}

# API resource for /telegram-bot.
resource "aws_api_gateway_resource" "telegram_bot_resource" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  parent_id   = aws_api_gateway_rest_api.telegram_bot_api.root_resource_id
  path_part   = "telegram-bot"
}

# API POST method for /telegram-bot.
resource "aws_api_gateway_method" "telegram_bot_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.telegram_bot_api.id
  resource_id   = aws_api_gateway_resource.telegram_bot_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integration of POST method with Lambda.
resource "aws_api_gateway_integration" "telegram_bot_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  resource_id = aws_api_gateway_resource.telegram_bot_resource.id
  http_method = aws_api_gateway_method.telegram_bot_post_method.http_method
  type        = "AWS_PROXY"
  integration_http_method = "POST"
  uri         = aws_lambda_function.telegram_bot.invoke_arn
}

# API Deployment.
resource "aws_api_gateway_deployment" "telegram_bot_deployment" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  depends_on  = [aws_api_gateway_integration.telegram_bot_post_integration]
  stage_name  = var.api_stage_name
}

# Allow API Gateway to invoke Lambda.
resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.telegram_bot.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.telegram_bot_api.execution_arn}/*/*"
}

# Output the API Gateway URL.
output "api_gateway_url" {
  value = aws_api_gateway_deployment.telegram_bot_deployment.invoke_url
  description = "The URL for the API Gateway endpoint."
}
