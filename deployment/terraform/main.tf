# Define the AWS provider and dynamically set the region based on a variable.
provider "aws" {
  region = var.aws_region
}

# IAM Role for the Lambda function, granting it necessary permissions to execute.
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}_${var.environment}_aws-iam-role_telegram-bot"

  # Define the trust relationship for the Lambda service to assume the role.
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com" # Grant Lambda permission to assume this role.
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach the basic Lambda execution policy to the IAM role.
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Define the Lambda function with its settings, environment variables, and permissions.
resource "aws_lambda_function" "telegram_bot" {
  function_name = "${var.project_name}_${var.environment}_aws-lambda-function_telegram-bot"
  role          = aws_iam_role.lambda_role.arn
  handler       = "lambda_function.lambda_handler"
  runtime       = "python3.13" # Specify the Python runtime for the function.
  filename      = "${path.module}/telegram_bot.zip" # The deployment package containing the Lambda function code.
  timeout       = 10 # The maximum time the function is allowed to run before timing out.

  # Define environment variables for the Lambda function.
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

  # Use the hash of the deployment package to detect changes and trigger updates.
  source_code_hash = filebase64sha256("${path.module}/telegram_bot.zip")
}

# Create an API Gateway to expose the Lambda function as an HTTP endpoint.
resource "aws_api_gateway_rest_api" "telegram_bot_api" {
  name = "${var.project_name}_${var.environment}_aws-api-gateway-rest-api_telegram-bot"
}

# Define a new resource under the API Gateway at the /telegram-bot path.
resource "aws_api_gateway_resource" "telegram_bot_resource" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  parent_id   = aws_api_gateway_rest_api.telegram_bot_api.root_resource_id
  path_part   = "telegram-bot"
}

# Create a POST method for the /telegram-bot resource.
resource "aws_api_gateway_method" "telegram_bot_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.telegram_bot_api.id
  resource_id   = aws_api_gateway_resource.telegram_bot_resource.id
  http_method   = "POST"
  authorization = "NONE" # No authorization is required for this example.
}

# Integrate the POST method with the Lambda function.
resource "aws_api_gateway_integration" "telegram_bot_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  resource_id = aws_api_gateway_resource.telegram_bot_resource.id
  http_method = aws_api_gateway_method.telegram_bot_post_method.http_method
  type        = "AWS_PROXY" # Use AWS Proxy integration to invoke the Lambda function directly.
  integration_http_method = "POST"
  uri         = aws_lambda_function.telegram_bot.invoke_arn
}

# Deploy the API Gateway to make the /telegram-bot endpoint available.
resource "aws_api_gateway_deployment" "telegram_bot_deployment" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  depends_on  = [aws_api_gateway_integration.telegram_bot_post_integration] # Ensure the integration is complete before deployment.
}

# Define the API Gateway stage for the deployment (e.g., test or prod).
resource "aws_api_gateway_stage" "telegram_bot_stage" {
  deployment_id = aws_api_gateway_deployment.telegram_bot_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.telegram_bot_api.id
  stage_name    = var.api_stage_name
}

# Grant API Gateway permission to invoke the Lambda function.
resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.telegram_bot.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.telegram_bot_api.execution_arn}/*/*"
}

# Output the API Gateway URL to access the Lambda function.
output "api_gateway_url" {
  value       = aws_api_gateway_stage.telegram_bot_stage.invoke_url
  description = "The URL for the API Gateway endpoint."
}

# Output the service account private key for debugging purposes.
output "debug_service_account_private_key" {
  value       = var.service_account_private_key
  description = "Debug output for the service_account_private_key variable."
}

# Configure the backend to store the Terraform state file in an S3 bucket.
terraform {
  backend "s3" {
    bucket         = "${var.project_name}-${var.environment}-terraform-state"
    key            = "${var.environment}/terraform.tfstate"
    region         = var.aws_region
    encrypt        = true # Ensure that the state file is encrypted.
  }
}
