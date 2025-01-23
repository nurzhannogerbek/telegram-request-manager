provider "aws" {
  region = var.aws_region # Use the AWS region from the variable.
}

# Define the IAM role for the Lambda function.
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}_${var.environment}_aws-iam-role_telegram-bot"

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

# Attach the AWS managed policy for basic Lambda execution to the IAM role.
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Define the Lambda function.
resource "aws_lambda_function" "telegram_bot" {
  function_name = "${var.project_name}_${var.environment}_aws-lambda-function_telegram-bot"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.13"
  filename      = "${path.module}/telegram_bot.zip"

  environment {
    variables = {
      TELEGRAM_BOT_TOKEN                        = var.telegram_bot_token
      ADMIN_CHAT_ID                             = var.admin_chat_id
      GOOGLE_SHEET_ID                           = var.google_sheet_id
      SERVICE_ACCOUNT_TYPE                      = var.service_account_type
      SERVICE_ACCOUNT_PROJECT_ID                = var.service_account_project_id
      SERVICE_ACCOUNT_PRIVATE_KEY_ID            = var.service_account_private_key_id
      SERVICE_ACCOUNT_PRIVATE_KEY               = var.service_account_private_key
      SERVICE_ACCOUNT_CLIENT_EMAIL              = var.service_account_client_email
      SERVICE_ACCOUNT_CLIENT_ID                 = var.service_account_client_id
      SERVICE_ACCOUNT_AUTH_URI                  = var.service_account_auth_uri
      SERVICE_ACCOUNT_TOKEN_URI                 = var.service_account_token_uri
      SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL    = var.service_account_auth_provider_cert_url
      SERVICE_ACCOUNT_CLIENT_CERT_URL           = var.service_account_client_cert_url
    }
  }
}

# Define the API Gateway for handling incoming HTTP POST requests.
resource "aws_api_gateway_rest_api" "telegram_bot_api" {
  name = "${var.project_name}_${var.environment}_aws-api-gateway-rest-api_telegram-bot"
}

# Define the API resource for the /telegram-bot path.
resource "aws_api_gateway_resource" "telegram_bot_resource" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  parent_id   = aws_api_gateway_rest_api.telegram_bot_api.root_resource_id
  path_part   = "telegram-bot"
}

# Create an HTTP POST method for the /telegram-bot resource.
resource "aws_api_gateway_method" "telegram_bot_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.telegram_bot_api.id
  resource_id   = aws_api_gateway_resource.telegram_bot_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

# Integrate the POST method with the Lambda function.
resource "aws_api_gateway_integration" "telegram_bot_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  resource_id = aws_api_gateway_resource.telegram_bot_resource.id
  http_method = aws_api_gateway_method.telegram_bot_post_method.http_method
  type        = "AWS_PROXY"
  integration_http_method = "POST"
  uri         = aws_lambda_function.telegram_bot.invoke_arn
}

# Deploy the API Gateway.
resource "aws_api_gateway_deployment" "telegram_bot_deployment" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  depends_on  = [aws_api_gateway_integration.telegram_bot_post_integration]
  stage_name  = var.api_stage_name
}

# Grant API Gateway permission to invoke the Lambda function.
resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.telegram_bot.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.telegram_bot_api.execution_arn}/*/*"
}

# Output the API Gateway URL.
output "api_gateway_url" {
  value       = aws_api_gateway_deployment.telegram_bot_deployment.invoke_url
  description = "The URL for the API Gateway endpoint."
}
