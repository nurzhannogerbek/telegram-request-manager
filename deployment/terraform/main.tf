# Define the AWS provider and the region to deploy the resources.
provider "aws" {
  region = var.aws_region # The region is dynamically set using a variable.
}

# IAM Role for the Lambda function to execute with necessary permissions.
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}_${var.environment}_aws-iam-role_telegram-bot" # Unique role name.

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com" # Allow the AWS Lambda service to assume this role.
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

# Attach the AWS-managed policy for basic Lambda execution permissions.
resource "aws_iam_role_policy_attachment" "lambda_policy_attachment" {
  role       = aws_iam_role.lambda_role.name # Attach the policy to the IAM role defined above.
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole" # AWS-managed policy for Lambda.
}

# Define the Lambda function itself.
resource "aws_lambda_function" "telegram_bot" {
  function_name = "${var.project_name}_${var.environment}_aws-lambda-function_telegram-bot" # Unique function name.
  role          = aws_iam_role.lambda_role.arn # IAM role to be assumed by the function.
  handler       = "lambda_function.lambda_handler" # Entry point for the Lambda function.
  runtime       = "python3.13" # Python runtime version for the function.
  filename      = "${path.module}/telegram_bot.zip" # Path to the zip file containing the Lambda code.
  timeout       = 10 # Set the timeout.

  # Set environment variables for the function.
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

  # Use the hash of the zip file to detect changes and trigger updates.
  source_code_hash = filebase64sha256("${path.module}/telegram_bot.zip")
}

# Create an API Gateway to expose the Lambda function as an HTTP endpoint.
resource "aws_api_gateway_rest_api" "telegram_bot_api" {
  name = "${var.project_name}_${var.environment}_aws-api-gateway-rest-api_telegram-bot" # API Gateway name.
}

# Define the /telegram-bot resource in the API Gateway.
resource "aws_api_gateway_resource" "telegram_bot_resource" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id # API Gateway ID.
  parent_id   = aws_api_gateway_rest_api.telegram_bot_api.root_resource_id # Parent resource (root).
  path_part   = "telegram-bot" # Path segment for the resource.
}

# Create a POST method for the /telegram-bot resource.
resource "aws_api_gateway_method" "telegram_bot_post_method" {
  rest_api_id   = aws_api_gateway_rest_api.telegram_bot_api.id # API Gateway ID.
  resource_id   = aws_api_gateway_resource.telegram_bot_resource.id # Resource ID.
  http_method   = "POST" # HTTP method for the endpoint.
  authorization = "NONE" # No authorization required.
}

# Link the POST method to the Lambda function.
resource "aws_api_gateway_integration" "telegram_bot_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  resource_id = aws_api_gateway_resource.telegram_bot_resource.id
  http_method = aws_api_gateway_method.telegram_bot_post_method.http_method
  type        = "AWS_PROXY" # Use AWS Proxy to directly invoke the Lambda function.
  integration_http_method = "POST"
  uri         = aws_lambda_function.telegram_bot.invoke_arn
}

# Deploy the API Gateway.
resource "aws_api_gateway_deployment" "telegram_bot_deployment" {
  rest_api_id = aws_api_gateway_rest_api.telegram_bot_api.id
  depends_on  = [aws_api_gateway_integration.telegram_bot_post_integration] # Ensure integration is complete first.
}

# Define the API Gateway stage (e.g., test, prod).
resource "aws_api_gateway_stage" "telegram_bot_stage" {
  deployment_id = aws_api_gateway_deployment.telegram_bot_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.telegram_bot_api.id
  stage_name    = var.api_stage_name # Use the environment name as the stage name.
}

# Grant the API Gateway permission to invoke the Lambda function.
resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway" # Unique statement ID.
  action        = "lambda:InvokeFunction" # Allow the invoke function action.
  function_name = aws_lambda_function.telegram_bot.arn # Lambda function ARN.
  principal     = "apigateway.amazonaws.com" # Principal service that is allowed to invoke.
  source_arn    = "${aws_api_gateway_rest_api.telegram_bot_api.execution_arn}/*/*" # ARN of the API Gateway.
}

# Output the API Gateway URL.
output "api_gateway_url" {
  value       = aws_api_gateway_stage.telegram_bot_stage.invoke_url # Full URL of the deployed API Gateway.
  description = "The URL for the API Gateway endpoint." # Description of the output value.
}

# Configure the Terraform backend to store the state file in an S3 bucket.
terraform {
  backend "s3" {
    bucket         = "${var.project_name}-${var.environment}-terraform-state" # S3 bucket for state files.
    key            = "${var.environment}/terraform.tfstate" # Path to the state file in the bucket.
    region         = var.aws_region # AWS region where the bucket is located.
    encrypt        = true # Enable encryption for the state file.
  }
}
