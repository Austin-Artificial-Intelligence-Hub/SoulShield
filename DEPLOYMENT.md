# Deployment Guide

## Prerequisites

1. AWS Account with appropriate permissions
2. AWS CLI configured (`aws configure`)
3. Python 3.11+ installed
4. AWS CDK installed (`npm install -g aws-cdk`)

## Step-by-Step Deployment

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Build Lambda Layer

```bash
chmod +x scripts/setup_layer.sh
./scripts/setup_layer.sh
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set:
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `AWS_REGION`: Target region (e.g., us-east-1)
- `LLM_PROVIDER`: Choose 'bedrock' or 'openai'
- `OPENAI_API_KEY`: If using OpenAI
- `SYSTEM_PROMPT`: Customize the assistant behavior
- `DATA_RETENTION_DAYS`: How long to keep chat history

### 5. Bootstrap CDK (First Time Only)

```bash
cdk bootstrap aws://YOUR_ACCOUNT_ID/YOUR_REGION
```

### 6. Deploy Stack

```bash
cdk deploy
```

This will output:
- API Gateway URL
- API Key ID

### 7. Retrieve API Key

```bash
aws apigateway get-api-key --api-key YOUR_KEY_ID --include-value
```

Or via AWS Console: API Gateway → API Keys → Show

### 8. Test the API

```bash
chmod +x scripts/test-api.sh
./scripts/test-api.sh https://YOUR_API_URL.execute-api.region.amazonaws.com/prod/ YOUR_API_KEY
```

## Using Bedrock

If using AWS Bedrock, ensure:

1. Bedrock is available in your region
2. You have model access enabled:
   - Go to AWS Console → Bedrock → Model access
   - Request access to Claude 3 Haiku

## Security Considerations

- API keys are stored in AWS Secrets Manager (via API Gateway)
- DynamoDB encryption at rest is enabled
- TLS 1.2+ enforced for all API calls
- No chat content logged to CloudWatch
- TTL automatically deletes old conversations

## Cost Estimation

Approximate costs (us-east-1):
- API Gateway: $3.50 per million requests
- Lambda: $0.20 per million requests (512MB, 1s avg)
- DynamoDB: $0.25 per GB stored + $1.25 per million writes
- Bedrock Claude Haiku: ~$0.25 per million input tokens

Typical usage (1000 conversations/day): ~$10-20/month

## Monitoring

View logs:
```bash
aws logs tail /aws/lambda/PrivacyChatbotStack-ChatHandler --follow
```

## Cleanup

To remove all resources:
```bash
cdk destroy
```

Note: DynamoDB table is retained by default for data safety.
