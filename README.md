# Telegram Request Manager

A Telegram bot that automates the handling of group join requests by collecting user data, validating inputs, and storing them in Google Sheets. The bot is optimized for AWS Lambda deployment, utilizing hot-start optimization by reusing connections, instances, and environment variables.

## Key Features

1. *Automated Join Request Handling*
   - Collects user data through an interactive questionnaire.
   - Validates inputs (email, phone number, age) to ensure correctness.
   - Automatically approves or denies join requests based on data completeness.

2. *Integration with Google Sheets*
   - Stores collected user responses and metadata for efficient management.

3. *Multi-Language Support*
   - Supports English, Russian, and Kazakh for user interactions.

4. *Optimized for AWS Lambda*
   - Uses hot-start optimizations by reusing resources.

5. *CI/CD with GitHub Actions and Terraform*
   - Automated deployment through GitHub Actions. 
   - Infrastructure as code managed via Terraform.

## User Interaction Flow

1. *Join Request*: The user initiates the join request by clicking "Join".
2. *Welcome Message*: The bot sends a welcome message prompting the user to select a language.
3. *Language Selection*: The user selects one of the supported languages.
4. *Privacy Policy*: The bot sends a privacy policy based on the selected language, with options to agree or decline.
   - If the user agrees, the questionnaire begins. 
   - If the user declines, the interaction ends.
5. *Questionnaire*: The bot asks for information like name, age, purpose of joining, etc., validating inputs along the way.
6. *Completion*: The bot either approves or denies the join request based on the data provided.

## Project Structure

```
telegram-request-manager
|-- .github
|   `-- workflows
|       `-- deploy.yml            # GitHub Actions CI/CD pipeline
|-- deployment
|   `-- terraform                 # Infrastructure as code using Terraform
|       |-- environments
|       |   |-- prod
|       |   |   `-- terraform.tfvars
|       |   `-- test
|       |       `-- terraform.tfvars
|       |-- main.tf
|       `-- variables.tf
|-- lambdas
|   `-- telegram_bot              # AWS Lambda function implementation
|       |-- __init__.py
|       |-- lambda_function.py    # Entry point for Lambda function
|       `-- requirements.txt      # Python dependencies for Lambda
|-- shared
|   `-- telegram_bot              # Shared modules for the bot
|       |-- __init__.py
|       |-- bootstrap.py          # Initializes shared resources
|       |-- config.py             # Configuration handling
|       |-- forms.py              # Questionnaire logic
|       |-- globals.py            # Global variables for shared access
|       |-- google_sheets.py      # Google Sheets interaction
|       |-- handlers.py           # Telegram bot event handlers
|       |-- localization.py       # Multilingual support
|       |-- logger.py             # Logging configuration
|       |-- main.py               # Core application logic
|       |-- utils.py              # Utility functions
|       `-- validation.py         # Input validation logic
|-- .gitignore                    # Git ignore rules
`-- README.md                     # Project documentation
```

## Google Sheets Integration

The bot uses Google Sheets to store user responses and metadata, enabling easy access and management.

### Sheets Structure

1. *Main Sheet*
   - Stores responses collected from users during the questionnaire. 
   - Columns:
     - `User ID`: Unique Telegram user ID.
     - `Full Name`: User's full name.
     - `Age`: User's age.
     - `Email`: User's email address.
     - `Phone`: User's phone number.
     - `Purpose`: Purpose for joining the group.
     - `Occupation`: The user's occupation or professional activity.
     - `Workplace`: The user's place of work or organization.
     - `City`: The city where the user resides.

2. *Metadata Sheet*
   - Tracks the current progress and state of each user.
   - Columns:
     - `User ID`: Unique Telegram user ID.
     - `Chat ID`: Chat ID associated with the user.
     - `Language`: Language preference of the user.
     - `Current Question Index`: Index of the current question in the questionnaire. 
     - `Responses`: JSON representation of responses.

## Environment Variables

The following environment variables are required and stored in GitHub Secrets:
- `TELEGRAM_BOT_TOKEN`
- `ADMIN_CHAT_ID`
- `GOOGLE_SHEET_ID`
- `SERVICE_ACCOUNT_TYPE`
- `SERVICE_ACCOUNT_PROJECT_ID`
- `SERVICE_ACCOUNT_PRIVATE_KEY_ID`
- `SERVICE_ACCOUNT_PRIVATE_KEY`
- `SERVICE_ACCOUNT_CLIENT_EMAIL`
- `SERVICE_ACCOUNT_CLIENT_ID`
- `SERVICE_ACCOUNT_AUTH_URI`
- `SERVICE_ACCOUNT_TOKEN_URI`
- `SERVICE_ACCOUNT_AUTH_PROVIDER_CERT_URL`
- `SERVICE_ACCOUNT_CLIENT_CERT_URL`
- `PRIVACY_POLICY_URL_RU`
- `PRIVACY_POLICY_URL_EN`
- `PRIVACY_POLICY_URL_KZ`
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_DEFAULT_REGION`

## CI/CD Pipeline

The project uses **GitHub Actions** for automated testing and deployment, with the [deploy.yml](.github/workflows/deploy.yml) workflow managing the entire process. The pipeline is designed to automate deployments to both test and production environments using **Terraform** for infrastructure as code.

### Pipeline Overview

1. **Triggering the Workflow**
    - The pipeline triggers on every push to the `main` branch and can also be manually triggered using the **GitHub Actions** interface.

2. **Workflow Steps**

    #### a. **Checkout Repository**
    The workflow begins by checking out the latest version of the repository to the GitHub runner using the `actions/checkout` action.

    #### b. **Setup Terraform**
    The `hashicorp/setup-terraform` action installs and configures **Terraform v1.5.0** to manage AWS resources, such as Lambda and API Gateway.

    #### c. **Package the Lambda Function**
    The Lambda function's code is packaged into a zip archive for deployment:
    - Install dependencies using `pip`.
    - Copy shared modules to the Lambda directory.
    - Zip the Lambda function and shared code.

    #### d. **Debugging and Verification**
    A partial debug of the service account private key is displayed to verify that the correct credentials are being used.

    #### e. **Terraform Initialization**
    Terraform is initialized with an S3 backend to store the state file securely.

    #### f. **Terraform Apply**
    The infrastructure is deployed using `terraform apply`. Environment-specific configurations are injected using `.tfvars` files.

3. **Environment Variables**
    - The pipeline retrieves environment-specific secrets and injects them as variables during deployment.
    - Variables include API keys, Google service account details, and privacy policy URLs for localization.

### Test and Production Deployments

- The **test deployment** (`deploy-test`) runs automatically on every push to `main`.
- The **production deployment** (`deploy-prod`) is disabled by default and requires manual activation. It depends on the successful completion of the test deployment.

### Infrastructure Components

- **AWS Lambda**: Hosts the Telegram bot.
- **API Gateway**: Exposes the Lambda function as an HTTP endpoint.
- **IAM Roles**: Grants the Lambda function permissions to execute and access AWS services.

### Terraform Configuration

The Terraform configuration, defined in the `main.tf` file, includes:
- AWS Lambda function
- IAM roles and policies
- API Gateway resources and stages
- Secure storage of the state file using S3

The environment-specific variables are defined in the following files:
- **Test:** `environments/test/terraform.tfvars`
- **Production:** `environments/prod/terraform.tfvars`

### Example Workflow Execution

#### **Test Deployment (deploy-test)**
1. Check out the repository code.
2. Install and configure Terraform.
3. Package the Lambda function.
4. Verify service account credentials.
5. Initialize and apply the Terraform configuration for the test environment.

#### **Production Deployment (deploy-prod)**
1. Requires manual activation.
2. Deploys the infrastructure with production-specific variables.

By leveraging Terraform and GitHub Actions, this CI/CD pipeline ensures reliable, repeatable, and automated deployments, reducing manual intervention and improving overall deployment efficiency.

## Setting Up the Project

This section outlines the prerequisites and step-by-step instructions to set up the project locally or deploy it to the cloud.

### Prerequisites

To get started, ensure you have the following prerequisites configured:

1. **Telegram Bot**
   - Go to [BotFather](https://t.me/BotFather) on Telegram.
   - Create a new bot by following the BotFather instructions:
     - `/newbot` to create a new bot.
     - Provide a name and a username for the bot (must end in `bot`).
     - BotFather will provide a **bot token**. Copy and securely store this token, as it will be used to authenticate the bot in the configuration.

2. **Google Sheets**
   - Create a new [Google Sheet](https://sheets.google.com).
   - The sheet should contain two sheets (tabs):
     - **Responses:** For storing user responses.
       - Columns: User ID, Full Name, Age, Email, Phone Number, Purpose, etc.
     - **Metadata:** For storing the state of user interactions.
       - Columns: User ID, Language, Current Question Index, Responses, Chat ID, Last Question.
   - Share the sheet with the **Google Service Account** (explained below) using its **client email** and provide "Editor" access.

3. **Google Service Account**
   - Go to [Google Cloud Console](https://console.cloud.google.com).
   - Create a new project (or use an existing one).
   - Enable the **Google Sheets API** and **Google Drive API** in the project.
   - Navigate to **APIs & Services > Credentials** and create a new **Service Account**.
   - Assign the role **Editor** to the service account.
   - Generate a **JSON key** for the service account:
     - Download the key and keep it securely stored.
     - The content of this file will be required for environment variables during deployment.
   - Note down the **service account’s client email**, as it is needed to share access to the Google Sheet.

4. **AWS Configuration**
   - Set up AWS credentials by configuring environment variables:
     - **AWS_ACCESS_KEY_ID:** The access key ID for an IAM user with permissions to deploy the Lambda function and API Gateway.
     - **AWS_SECRET_ACCESS_KEY:** The secret access key associated with the access key ID.
     - **AWS_DEFAULT_REGION:** The region where you want to deploy the infrastructure (e.g., `eu-central-1`).

   - Alternatively, configure AWS credentials locally using the AWS CLI:
     ```bash
     aws configure
     ```

   - Ensure the IAM user has the necessary permissions for:
     - AWS Lambda
     - Amazon API Gateway
     - Amazon S3 (for storing the Terraform state file)

## Setting the Webhook

To connect the bot to the API Gateway, use the following command:
```
curl -X POST "https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/setWebhook" \
     -d "url=https://<api-id>.execute-api.<region>.amazonaws.com/<enviroment>/telegram-bot"
```

## License

This project is licensed under the [MIT License](LICENSE).  
Feel free to use, modify, and distribute the code as described in the license.

