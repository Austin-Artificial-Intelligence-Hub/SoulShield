# SoulShield - Trauma-Informed AI Support Coach

A secure, privacy-first mental health support assistant built on AWS with intelligent routing, trauma-informed responses, and comprehensive security features. SoulShield uses an agentic pipeline with LangSmith-managed prompts to provide personalized, contextual support.

## 🌟 Features

### AI Agents (LangSmith-Managed)
- 🧠 **Session Greeting Agent**: Personalized welcome messages for returning users based on past session summaries
- 🎯 **Routing Agent**: Intelligent message classification (mode, privacy context, risk level)
- 💚 **Support Coach**: Trauma-informed responses with mode-specific behavior (grounding, therapy prep, crisis resources)
- 🛡️ **Safety Fallback Agent**: Secure fallback responses when other agents fail

### Security & Privacy
- 🔐 **Client-Side Encryption**: AES-256-GCM encryption with PBKDF2 key derivation
- 🛡️ **XSS Protection**: Content Security Policy, Trusted Types, HTML sanitization
- 🔒 **Password Hashing**: PBKDF2-HMAC-SHA256 with 100,000 iterations
- 📦 **AWS Encryption**: DynamoDB encryption at rest (AWS-managed)
- 🗑️ **Auto-Deletion**: Data automatically deleted after 30 days

### Infrastructure
- ⚡ **Serverless**: AWS Lambda, API Gateway, DynamoDB
- 🤖 **Multiple LLM Support**: AWS Bedrock (Claude) or OpenAI
- 📊 **Chat Summaries**: Automatic conversation summaries for long chats
- 🌐 **Dual UI**: Beautiful Web interface + Streamlit alternative

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              WEB UI (Secure)                                │
│  ┌──────────────┐  ┌───────────────┐  ┌─────────────┐  ┌─────────────────┐ │
│  │  encryption  │  │   sanitize    │  │  dom-utils  │  │    app.js       │ │
│  │    (AES)     │  │    (XSS)      │  │(TrustedType)│  │  (main logic)   │ │
│  └──────────────┘  └───────────────┘  └─────────────┘  └─────────────────┘ │
│                              Content Security Policy                        │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ HTTPS
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                            API Gateway + API Key                             │
└──────────────────────────────────┬───────────────────────────────────────────┘
                                   │
                                   ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Lambda Function (Python)                             │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                        AGENTIC PIPELINE                                 │ │
│  │                                                                         │ │
│  │  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐             │ │
│  │  │   Session    │    │   Routing    │    │   Support    │             │ │
│  │  │   Greeting   │───▶│    Agent     │───▶│    Coach     │             │ │
│  │  │   Agent      │    │              │    │              │             │ │
│  │  └──────────────┘    └──────────────┘    └──────────────┘             │ │
│  │         │                   │                    │                     │ │
│  │         │                   │                    │                     │ │
│  │         │                   ▼                    ▼                     │ │
│  │         │            ┌──────────────┐    ┌──────────────┐             │ │
│  │         │            │   LangSmith  │    │    Safety    │             │ │
│  │         │            │   Prompts    │    │   Fallback   │             │ │
│  │         │            └──────────────┘    └──────────────┘             │ │
│  └─────────┼───────────────────────────────────────────────────────────────┘ │
│            │                                                                  │
└────────────┼──────────────────────────────────────────────────────────────────┘
             │
   ┌─────────┼─────────────────────────────────────────────┐
   │         │                                             │
   ▼         ▼                                             ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   DynamoDB      │    │   DynamoDB      │    │  OpenAI / AWS   │
│  Chat History   │    │ Users & Summary │    │    Bedrock      │
│   (Encrypted)   │    │   (Encrypted)   │    │   (Claude AI)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Agentic Pipeline Flow

1. **Session Greeting** (for returning users): Generates personalized welcome based on past session summaries
2. **Routing Agent**: Classifies message → `{mode, privacy_context, risk_level}`
3. **Support Coach**: Generates trauma-informed response based on routing
4. **Safety Fallback**: Provides safe response if other agents fail

## 🔒 Privacy & Security Features

### Client-Side Security (Web UI)
- **AES-256-GCM Encryption**: Messages encrypted before leaving the browser
- **PBKDF2 Key Derivation**: 100,000 iterations for password-derived keys
- **Content Security Policy**: No inline scripts, strict source restrictions
- **Trusted Types**: DOM-level XSS protection for modern browsers
- **HTML Sanitization**: All user content sanitized before rendering
- **Subresource Integrity**: External scripts verified with SRI hashes

### Server-Side Security (AWS)
- **Encryption at Rest**: DynamoDB with AWS-managed AES-256 encryption
- **Encryption in Transit**: TLS 1.2+ for all API communications
- **Secure Password Storage**: PBKDF2-HMAC-SHA256 with salt (100,000 iterations)
- **Data Minimization**: Only stores essential conversation data
- **Auto-Deletion**: All data automatically deleted after 30 days (configurable)
- **No Content Logging**: Chat messages never appear in CloudWatch logs
- **User Isolation**: Complete separation between user accounts
- **API Key Authentication**: Rate-limited API access
- **Session Tokens**: 24-hour expiring authentication tokens

### Bystander Safety (Trauma-Informed)
- **Privacy Context Detection**: Routing agent detects if user may be monitored
- **Bystander-Safe Language**: Neutral, everyday wellness wording when privacy unknown
- **No Escalation**: Never takes actions on user's behalf
- **User Autonomy**: Offers choices, not instructions

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

**Option A: Secure Web UI (Recommended)**
```bash
# Navigate to web directory and start server
cd web
python3 -m http.server 8080
```
Open http://localhost:8080 in your browser

**Option B: Streamlit UI**
```bash
# Install Streamlit dependencies
pip install -r streamlit_requirements.txt

# Launch the chat interface
streamlit run streamlit_app.py
```
Open http://localhost:8501 in your browser

### 6. Use Your Chatbot

1. Register a new account or login
2. Start chatting with your AI support coach!
3. The system will:
   - Route your message through the agentic pipeline
   - Detect your emotional state and privacy context
   - Respond with appropriate trauma-informed support

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
│   └── chatbot_stack.py       # AWS infrastructure definition
├── lambda/
│   ├── chat/
│   │   ├── index.py           # Main Lambda handler (agentic pipeline)
│   │   ├── llm_provider.py    # LLM integration & agent functions
│   │   └── requirements.txt   # Lambda dependencies
│   └── layer/                 # Shared Lambda layer
├── web/                        # Secure Web UI
│   ├── index.html             # Main HTML (with CSP)
│   └── js/
│       ├── app.js             # Main application logic
│       ├── config.js          # API configuration
│       ├── encryption.js      # Client-side AES-256 encryption
│       ├── sanitize.js        # HTML sanitization (XSS protection)
│       └── dom-utils.js       # Safe DOM manipulation (Trusted Types)
├── scripts/
│   ├── setup_layer.sh         # Build Lambda layer
│   ├── test_api.py            # API testing script
│   ├── single_turn_bystander.jsonl   # Evaluation dataset
│   └── multiturn_scenarios.json      # Multi-turn test scenarios
├── streamlit_app.py           # Alternative Streamlit UI
├── telegram_bot/              # Telegram bot integration
├── requirements.txt           # CDK dependencies
└── streamlit_requirements.txt # Streamlit UI dependencies
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