# Quick Start Guide

## What You Have Now

✅ Node.js installed
✅ AWS CDK installed  
✅ Python dependencies installed
✅ Lambda layer built

## Next Steps to Deploy

### 1. Configure AWS Credentials

Make sure AWS CLI is configured:
```bash
aws configure
```

Enter your:
- AWS Access Key ID
- AWS Secret Access Key
- Default region (e.g., us-east-1)
- Default output format (json)

### 2. Create .env File

```bash
cp .env.example .env
```

Edit `.env` and set:
```bash
AWS_ACCOUNT_ID=123456789012  # Your AWS account ID
AWS_REGION=us-east-1
LLM_PROVIDER=bedrock  # or 'openai'
DATA_RETENTION_DAYS=30
SYSTEM_PROMPT=You are a helpful AI assistant for customer service and general questions.
```

To get your AWS Account ID:
```bash
aws sts get-caller-identity --query Account --output text
```

### 3. Bootstrap CDK (First Time Only)

```bash
cdk bootstrap
```

### 4. Deploy to AWS

```bash
cdk deploy
```

This will:
- Create DynamoDB table
- Deploy Lambda function
- Set up API Gateway
- Create API key

**Save the outputs!** You'll see:
- API URL (e.g., https://abc123.execute-api.us-east-1.amazonaws.com/prod/)
- API Key ID

### 5. Get Your API Key

```bash
# Use the API Key ID from the deployment output
aws apigateway get-api-key --api-key <YOUR_KEY_ID> --include-value --query 'value' --output text
```

### 6. Test the API

```bash
# Using Python script
python scripts/test_api.py <API_URL> <API_KEY>

# Or using curl
curl -X POST https://YOUR_API_URL/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{"message": "Hello!"}'
```

### 7. Run Streamlit Interface

```bash
# Install Streamlit
pip install -r streamlit_requirements.txt

# Run the app
streamlit run streamlit_app.py
```

Then:
1. Browser opens at http://localhost:8501
2. Enter your API URL and API Key in the sidebar
3. Start chatting!

## Using AWS Bedrock

If you choose `LLM_PROVIDER=bedrock`:

1. Go to AWS Console → Bedrock
2. Click "Model access" in left menu
3. Request access to "Claude 3 Haiku"
4. Wait for approval (usually instant)

## Troubleshooting

### "No AWS credentials found"
Run `aws configure` and enter your credentials

### "Account not bootstrapped"
Run `cdk bootstrap`

### "Access denied to Bedrock"
Enable model access in AWS Bedrock console

### "Module not found"
Make sure you're in the virtual environment:
```bash
source venv/bin/activate  # or soul-env/bin/activate
```

## Cost Estimate

With Bedrock Claude Haiku:
- ~$0.25 per 1M input tokens
- ~$1.25 per 1M output tokens
- DynamoDB: ~$0.25/GB + $1.25/M writes
- Lambda: ~$0.20/M requests
- API Gateway: ~$3.50/M requests

**Typical usage (1000 chats/day): $10-20/month**

## What This Is For

This is a **general-purpose chatbot** for:
- Customer service
- Educational Q&A
- General assistance
- Information lookup

It is NOT for therapy, medical advice, or sensitive personal topics.
