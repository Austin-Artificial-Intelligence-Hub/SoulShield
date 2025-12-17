# SoulShield - Privacy-Focused AI Chatbot with User Memory

A secure, privacy-first conversational AI assistant built on AWS with user authentication and persistent memory through chat summaries. SoulShield protects your conversations while providing intelligent, personalized assistance.

## 🌟 Features

- 🔐 **User Authentication**: Secure username/password accounts with PBKDF2 hashing
- 💬 **Persistent Memory**: AI remembers conversations through intelligent summaries
- 🔒 **Privacy-First**: End-to-end encryption, auto-deletion, minimal logging
- ⚡ **Serverless**: Built on AWS Lambda, API Gateway, and DynamoDB
- 🤖 **Multiple LLM Support**: AWS Bedrock (Claude) or OpenAI
- 📊 **Chat Summaries**: Automatic conversation summaries for long chats
- 🌐 **Web Interface**: Beautiful Streamlit-based chat interface

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────┐    ┌─────────────────┐
│   Streamlit     │───▶│ API Gateway  │───▶│ Lambda Function │
│   Frontend      │    │   + API Key  │    │   (Python)      │
└─────────────────┘    └──────────────┘    └─────────────────┘
                                                     │
                              ┌──────────────────────┼──────────────────────┐
                              │                      │                      │
                              ▼                      ▼                      ▼
                    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
                    │   DynamoDB      │    │   DynamoDB      │    │   AWS Bedrock   │
                    │  Chat History   │    │ Users & Summary │    │   (Claude AI)   │
                    │   (Encrypted)   │    │   (Encrypted)   │    │                 │
                    └─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔒 Privacy & Security Features

- **Encryption at Rest**: All DynamoDB tables use AWS-managed AES-256 encryption
- **Encryption in Transit**: TLS 1.2+ for all API communications
- **Secure Password Storage**: PBKDF2 hashing with salt (100,000 iterations)
- **Data Minimization**: Only stores essential conversation data
- **Auto-Deletion**: All data automatically deleted after 30 days (configurable)
- **No Content Logging**: Chat messages never appear in CloudWatch logs
- **User Isolation**: Complete separation between user accounts
- **API Key Authentication**: Rate-limited API access
- **Session Tokens**: 24-hour expiring authentication tokens

## 🚀 Quick Start

### Prerequisites

- AWS Account with CLI configured
- Python 3.11+
- Node.js 18+ (for AWS CDK)
- Git

### 1. Clone and Setup

```bash
git clone git@github.com:Austin-Artificial-Intelligence-Hub/SoulShield.git
cd SoulShield

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install -g aws-cdk
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your AWS account details
```

Required environment variables:
- `AWS_ACCOUNT_ID`: Your AWS account ID
- `AWS_REGION`: Target AWS region (e.g., us-east-1)
- `LLM_PROVIDER`: 'bedrock' or 'openai'
- `OPENAI_API_KEY`: Required if using OpenAI
- `DATA_RETENTION_DAYS`: Data retention period (default: 30)
- `SYSTEM_PROMPT`: Customize AI behavior

### 3. Build and Deploy

```bash
# Build Lambda dependencies
chmod +x scripts/setup_layer.sh
./scripts/setup_layer.sh

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy to AWS
cdk deploy
```

### 4. Enable AWS Bedrock (if using Bedrock)

1. Go to [AWS Bedrock Console](https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess)
2. Click "Manage model access"
3. Enable "Claude 3 Haiku"
4. Submit the use case form

### 5. Run the Web Interface

```bash
# Install Streamlit dependencies
pip install -r streamlit_requirements.txt

# Launch the chat interface
streamlit run streamlit_app.py
```

### 6. Use Your Chatbot

1. Open http://localhost:8501 in your browser
2. Enter your API URL and API Key (from CDK deployment output)
3. Register a new account or login
4. Start chatting with your AI assistant!

## 📖 Usage

### Creating an Account
1. Click "Register" in the sidebar
2. Choose a username and secure password
3. Click "Create Account"

### Chatting
1. Login with your credentials
2. Type messages in the chat input
3. The AI remembers context within each session
4. After 10+ messages, automatic summaries are generated

### Viewing Chat History
1. Click "View Chat Summaries" in the sidebar
2. See AI-generated summaries of your past conversations
3. Each summary includes session info and key discussion points

### Privacy Controls
- **New Session**: Start fresh conversation (clears current context)
- **Logout**: Clears local session data
- **Auto-Deletion**: All data automatically deleted after 30 days

## 🛠️ Development

### Project Structure

```
├── app.py                      # CDK app entry point
├── stacks/
│   └── chatbot_stack.py       # Infrastructure definition
├── lambda/
│   ├── chat/
│   │   ├── index.py           # Main Lambda handler
│   │   ├── llm_provider.py    # LLM integration
│   │   └── requirements.txt   # Lambda dependencies
│   └── layer/                 # Shared Lambda layer
├── scripts/
│   ├── setup_layer.sh         # Build Lambda layer
│   └── test_api.py           # API testing script
├── streamlit_app.py           # Web interface
├── requirements.txt           # CDK dependencies
└── streamlit_requirements.txt # UI dependencies
```

### API Endpoints

- `POST /auth/register` - Create new user account
- `POST /auth/login` - User authentication
- `POST /chat` - Send message to AI
- `GET /summaries` - Retrieve user's chat summaries

### Testing

```bash
# Test API directly
python scripts/test_api.py <API_URL> <API_KEY>

# Test Bedrock access
python test_bedrock.py
```

### Customization

#### Change AI Behavior
Edit `SYSTEM_PROMPT` in `.env`:
```bash
SYSTEM_PROMPT="You are a helpful customer service assistant for Acme Corp."
```

#### Adjust Data Retention
```bash
DATA_RETENTION_DAYS=7  # Keep data for 7 days instead of 30
```

#### Switch to OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your-openai-key-here
```

## 💰 Cost Estimation

Typical usage (1000 conversations/day):

| Service | Cost |
|---------|------|
| AWS Bedrock (Claude Haiku) | ~$5-10/month |
| DynamoDB | ~$2-5/month |
| Lambda | ~$1-2/month |
| API Gateway | ~$3-5/month |
| **Total** | **~$11-22/month** |

## 🔧 Troubleshooting

### Common Issues

**"Bedrock access denied"**
- Enable Claude 3 Haiku in AWS Bedrock console
- Ensure you're in a supported region

**"Invalid API key"**
- Retrieve correct key: `aws apigateway get-api-key --api-key <KEY_ID> --include-value`
- Check API Gateway console

**"Failed to load summaries"**
- Check Lambda logs: `aws logs tail /aws/lambda/PrivacyChatbotStack-ChatHandler* --follow`
- Ensure you have 10+ messages in a conversation

### Monitoring

```bash
# View Lambda logs
aws logs tail /aws/lambda/PrivacyChatbotStack-ChatHandler* --follow

# Check DynamoDB tables
aws dynamodb list-tables --query 'TableNames[?contains(@, `PrivacyChatbot`)]'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Add tests if applicable
5. Commit: `git commit -am 'Add feature'`
6. Push: `git push origin feature-name`
7. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- AWS CDK team for excellent infrastructure-as-code tools
- Anthropic for Claude AI models
- Streamlit for the beautiful web interface framework
- The open-source community for inspiration and tools

## 📞 Support

- 🐛 Issues: [GitHub Issues](https://github.com/Austin-Artificial-Intelligence-Hub/SoulShield/issues)
- 📖 Documentation: [Wiki](https://github.com/Austin-Artificial-Intelligence-Hub/SoulShield/wiki)
- 🏢 Organization: [Austin AI Hub](https://github.com/Austin-Artificial-Intelligence-Hub)

---

**Built with privacy in mind** 🔒 • **User accounts** 👥 • **Chat summaries** 📊 • **Auto-deleted after 30 days** ⏰