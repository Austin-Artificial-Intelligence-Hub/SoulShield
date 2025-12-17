# Streamlit Chat Interface Guide

## What This Is

A **general-purpose chatbot interface** for customer service, education, and general assistance. This is NOT a therapy tool - it's a conversational AI for everyday use cases.

## Setup

### 1. Install Streamlit Dependencies

```bash
pip install -r streamlit_requirements.txt
```

### 2. Run the Streamlit App

```bash
streamlit run streamlit_app.py
```

This will:
- Start a local web server (usually at http://localhost:8501)
- Open your browser automatically
- Show the chat interface

### 3. Configure the App

In the sidebar, enter:
- **API URL**: Your AWS API Gateway URL (from CDK deployment output)
- **API Key**: Your API key (retrieve from AWS Console)

Example API URL:
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod/
```

### 4. Get Your API Key

After deploying with `cdk deploy`, get your API key:

```bash
# Get the API Key ID from CDK output, then:
aws apigateway get-api-key --api-key YOUR_KEY_ID --include-value --query 'value' --output text
```

Or via AWS Console:
1. Go to API Gateway
2. Click "API Keys" in the left menu
3. Click your key name
4. Click "Show" to reveal the key value

## Features

- 💬 Real-time chat interface
- 🔄 Session management (start new conversations)
- 🔒 Privacy-focused (encrypted, auto-deleted)
- 📱 Responsive design
- ⚙️ Easy configuration via sidebar

## Usage

1. Type your message in the chat input at the bottom
2. Press Enter or click Send
3. The AI will respond based on your configured system prompt
4. Continue the conversation - it remembers context within the session
5. Click "New Session" to start fresh

## Customization

### Change System Prompt

Edit your `.env` file before deploying:

```bash
SYSTEM_PROMPT="You are a helpful customer service assistant for Acme Corp. Be friendly and professional."
```

Then redeploy:
```bash
cdk deploy
```

### Styling

Edit `streamlit_app.py` to customize:
- Colors and theme
- Page title and icon
- Layout and components

## Running in Production

### Option 1: Streamlit Cloud (Free)

1. Push your code to GitHub
2. Go to https://streamlit.io/cloud
3. Connect your repository
4. Deploy (it's free for public apps)

### Option 2: Docker

```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.11-slim
WORKDIR /app
COPY streamlit_app.py .
COPY streamlit_requirements.txt .
RUN pip install -r streamlit_requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF

# Build and run
docker build -t chatbot-ui .
docker run -p 8501:8501 chatbot-ui
```

### Option 3: AWS (ECS/Fargate)

Deploy the Docker container to AWS ECS for a fully AWS-hosted solution.

## Troubleshooting

### "Please configure API URL and API Key"
- Make sure you've entered both values in the sidebar
- Check that the URL ends with `/prod/` or your stage name

### "Connection error"
- Verify your API URL is correct
- Check that your API is deployed (`cdk deploy`)
- Ensure your AWS region is correct

### "403 Forbidden"
- Your API key is incorrect
- Retrieve the correct key from AWS Console

### "500 Internal Server Error"
- Check CloudWatch logs for your Lambda function
- Verify Bedrock access or OpenAI API key is configured
- Check Lambda environment variables

## Privacy Notes

- Messages are only stored in your AWS account
- Automatic deletion after 30 days (configurable)
- No third-party analytics or tracking
- All data encrypted in transit and at rest

## Local Development

To test without deploying to AWS, you can run the Lambda function locally:

```bash
# Install SAM CLI
brew install aws-sam-cli  # macOS

# Test Lambda locally
sam local start-api
```

Then point Streamlit to `http://localhost:3000`
