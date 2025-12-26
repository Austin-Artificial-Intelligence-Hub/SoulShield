# SoulShield Technical Documentation

> **A Covert Emotional Support Companion for Survivors of Human Trafficking**

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture](#architecture)
3. [Multi-Agent AI Pipeline](#multi-agent-ai-pipeline)
4. [LangSmith Integration](#langsmith-integration)
5. [Security Layers](#security-layers)
6. [Backend Infrastructure](#backend-infrastructure)
7. [Frontend Implementation](#frontend-implementation)
8. [API Reference](#api-reference)
9. [Deployment](#deployment)

---

## System Overview

SoulShield is a trauma-informed AI support system designed for survivors who cannot speak freely. The system uses a multi-agent architecture to:

- **Detect privacy context** — Identify when someone might be monitoring the user
- **Classify distress levels** — Route to appropriate support modes
- **Generate bystander-safe responses** — Use neutral language when privacy is compromised
- **Provide grounding techniques** — Help users regulate their nervous system

### Key Differentiators

| Feature | Traditional Therapy Apps | SoulShield |
|---------|-------------------------|------------|
| Language | Clinical terminology | Bystander-safe, neutral language |
| Detection | None | Privacy context detection |
| Monitoring | Obvious app interface | Looks like generic wellness app |
| Availability | Business hours | 24/7 |
| Data | Often stored indefinitely | Auto-deletes after 30 days |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   Web UI    │  │   Voice     │  │   Dark      │              │
│  │  (Vercel)   │  │   I/O       │  │   Mode      │              │
│  └──────┬──────┘  └──────┬──────┘  └─────────────┘              │
│         │                │                                       │
│         ▼                ▼                                       │
│  ┌─────────────────────────────────────────────────┐            │
│  │         Client-Side Security Layer              │            │
│  │  • AES-256-GCM Encryption                       │            │
│  │  • Content Security Policy                      │            │
│  │  • Trusted Types                                │            │
│  │  • HTML Sanitization                            │            │
│  └─────────────────────────┬───────────────────────┘            │
└────────────────────────────┼────────────────────────────────────┘
                             │ HTTPS
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS API GATEWAY                               │
│              (API Key Authentication)                            │
└─────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS LAMBDA                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                 AGENTIC PIPELINE                         │    │
│  │                                                          │    │
│  │   ┌──────────┐    ┌──────────┐    ┌──────────┐          │    │
│  │   │ ROUTING  │───▶│ SUPPORT  │───▶│ SAFETY   │          │    │
│  │   │  AGENT   │    │  COACH   │    │ FALLBACK │          │    │
│  │   └──────────┘    └──────────┘    └──────────┘          │    │
│  │                                                          │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│  │   LangSmith  │    │   OpenAI     │    │   Bedrock    │       │
│  │   (Prompts)  │    │   GPT-4      │    │   Claude     │       │
│  └──────────────┘    └──────────────┘    └──────────────┘       │
└─────────────────────────────┬───────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AWS DYNAMODB                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ ChatHistory  │  │    Users     │  │ ChatSummaries│           │
│  │  (30-day TTL)│  │ (Hashed PWD) │  │              │           │
│  └──────────────┘  └──────────────┘  └──────────────┘           │
│                 (AWS-Managed Encryption at Rest)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Multi-Agent AI Pipeline

SoulShield uses a sequential multi-agent pipeline where each agent has a specific responsibility.

### Agent 1: Routing Agent (`routing_agent_prompt`)

**Purpose:** Classify incoming messages to determine the appropriate response strategy.

**Input:**
```json
{
  "user_message": "He might check my phone. I can't risk obvious messages.",
  "conversation_history": [...]
}
```

**Output (Structured JSON):**
```json
{
  "mode": "support",
  "privacy_context": "bystander_present",
  "risk_level": "medium"
}
```

**Classification Categories:**

| Field | Possible Values | Description |
|-------|----------------|-------------|
| `mode` | `support`, `grounding`, `crisis` | Type of support needed |
| `privacy_context` | `private`, `bystander_possible`, `bystander_present` | Privacy level detected |
| `risk_level` | `low`, `medium`, `high` | Urgency assessment |

**Detection Signals:**
- "He might check my phone" → `bystander_present`
- "I'm alone right now" → `private`
- "Someone is watching" → `bystander_present`
- "I feel like I can't breathe" → `grounding` mode

---

### Agent 2: Support Coach (`support_coach`)

**Purpose:** Generate trauma-informed responses based on routing classification.

**Input:**
```json
{
  "user_message": "I'm feeling really anxious",
  "mode": "support",
  "privacy_context": "private",
  "conversation_history": [...]
}
```

**Output (Structured JSON):**
```json
{
  "response_text": "I hear that you're feeling anxious right now. That sounds really difficult. Would you like to try a quick grounding exercise together, or would it help to talk about what's bringing up these feelings?",
  "options": [
    "Try a grounding exercise",
    "Talk about what's happening"
  ]
}
```

**Response Principles:**
1. **Bystander-Safe Mode:** When `privacy_context` is not `private`:
   - Uses neutral wellness language
   - Avoids words: "abuse", "escape", "police", "violence", "trafficking"
   - Looks like a generic mindfulness app

2. **Trauma-Informed Approach:**
   - Reflects user's words back
   - Offers choices, never commands
   - Validates feelings without judgment
   - Respects user's pace and boundaries

3. **Grounding Mode:**
   - Guides breathing exercises (4-4-4 or box breathing)
   - 5-4-3-2-1 sensory grounding
   - Simple, clear instructions

---

### Agent 3: Safety Fallback (`safety_fallback`)

**Purpose:** Provide a safe, generic response if the main pipeline fails.

**Trigger Conditions:**
- Support Coach returns invalid JSON
- API timeout or error
- Unexpected exception

**Output:**
```json
{
  "response_text": "I'm here with you. Take a moment if you need it. When you're ready, I'm listening.",
  "options": []
}
```

**Design Philosophy:**
- Never fails silently
- Always provides a calming presence
- Avoids anything that could cause distress
- Buys time for user without escalating

---

### Pipeline Flow

```python
def run_chat_pipeline(user_message, conversation_history):
    # Step 1: Route the message
    routing = run_routing_agent(user_message, conversation_history)
    
    # Step 2: Generate response based on routing
    try:
        response = run_support_coach(
            user_message=user_message,
            mode=routing['mode'],
            privacy_context=routing['privacy_context'],
            conversation_history=conversation_history
        )
    except Exception:
        # Step 3: Fallback if coach fails
        response = run_safety_fallback()
    
    return {
        'response_text': response['response_text'],
        'options': response.get('options', []),
        'routing': routing
    }
```

---

## LangSmith Integration

### Prompt Management

All prompts are stored and versioned in LangSmith, allowing:
- **A/B testing** of prompt variations
- **Version control** for prompt changes
- **Tracing** of all LLM calls
- **Evaluation** against datasets

### Prompts Used

| Prompt Name | Purpose | Owner |
|------------|---------|-------|
| `routing_agent_prompt` | Classify user messages | LangSmith Hub |
| `support_coach` | Generate therapeutic responses | LangSmith Hub |
| `safety_fallback` | Emergency fallback response | LangSmith Hub |

### Pulling Prompts

```python
from langsmith import Client

ls_client = Client()
prompt = ls_client.pull_prompt("routing_agent_prompt")
formatted = prompt.format(user_message=message, history=history)
```

### Evaluation Dataset

**Dataset:** `SingleTurn_Bystander`

Contains test cases for evaluating bystander-safe responses:

```json
{
  "inputs": {
    "user_message": "He reads all my messages. I need to be careful."
  },
  "reference": {
    "mode": "support",
    "privacy_context": "bystander_present",
    "risk_level": "medium"
  }
}
```

### Metrics Tracked

| Metric | Description |
|--------|-------------|
| Routing Accuracy | % of correct mode/privacy/risk classifications |
| Schema Compliance | % of responses with valid JSON structure |
| Bystander Safety | % of responses avoiding trigger words when bystander detected |
| Fallback Usage | % of responses requiring fallback agent |
| Latency | Response time in milliseconds |

---

## Security Layers

SoulShield implements defense-in-depth with multiple security layers.

### Layer 1: Client-Side Encryption

**Technology:** AES-256-GCM with PBKDF2 Key Derivation

```javascript
// Key derivation from user password
async function deriveKey(password, salt) {
    const keyMaterial = await crypto.subtle.importKey(
        'raw',
        new TextEncoder().encode(password),
        'PBKDF2',
        false,
        ['deriveBits', 'deriveKey']
    );
    
    return crypto.subtle.deriveKey(
        {
            name: 'PBKDF2',
            salt: salt,
            iterations: 100000,
            hash: 'SHA-256'
        },
        keyMaterial,
        { name: 'AES-GCM', length: 256 },
        false,
        ['encrypt', 'decrypt']
    );
}
```

**Properties:**
- Messages encrypted before leaving browser
- Server never sees plaintext
- Only user with password can decrypt
- Each message uses unique IV (Initialization Vector)

---

### Layer 2: XSS Protection

**Content Security Policy (CSP):**
```html
<meta http-equiv="Content-Security-Policy" content="
    default-src 'self';
    script-src 'self';
    style-src 'self' 'unsafe-inline' https://fonts.googleapis.com;
    font-src https://fonts.gstatic.com;
    connect-src 'self' https://*.execute-api.us-east-1.amazonaws.com;
    img-src 'self' data:;
    frame-ancestors 'none'
">
```

**Trusted Types:**
```javascript
const policy = trustedTypes.createPolicy('soulshield', {
    createHTML: (input) => DOMPurify.sanitize(input)
});
```

**HTML Sanitization:**
- All user content sanitized before rendering
- Removes script tags, event handlers, dangerous attributes
- Uses DOMPurify library

---

### Layer 3: Transport Security

| Component | Protection |
|-----------|-----------|
| Frontend ↔ API Gateway | HTTPS/TLS 1.3 |
| API Gateway ↔ Lambda | AWS internal (encrypted) |
| Lambda ↔ DynamoDB | AWS internal (encrypted) |
| Lambda ↔ OpenAI | HTTPS/TLS |

---

### Layer 4: Authentication

**Password Storage:**
```python
import hashlib
import os

def hash_password(password):
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        100000
    )
    return salt + key  # Store both together
```

**Session Tokens:**
- Simple token format: `base64(username:timestamp)`
- Expires after 24 hours
- Verified on each request

**API Key:**
- AWS API Gateway API Key required for all requests
- Rate limited via Usage Plans

---

### Layer 5: Data Protection

**DynamoDB Encryption:**
- AWS-managed encryption at rest
- All tables encrypted by default

**Data Retention:**
- 30-day TTL (Time-To-Live) on all messages
- Automatic deletion by DynamoDB
- No manual intervention required

**Data Minimization:**
- No PII required for registration
- Anonymous usernames allowed
- No email or phone required

---

### Security Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                           │
├─────────────────────────────────────────────────────────────┤
│  🔐 Layer 5: Data Protection                                │
│     └─ DynamoDB encryption, 30-day TTL, data minimization   │
├─────────────────────────────────────────────────────────────┤
│  🔑 Layer 4: Authentication                                 │
│     └─ PBKDF2 password hashing, session tokens, API keys    │
├─────────────────────────────────────────────────────────────┤
│  🔒 Layer 3: Transport Security                             │
│     └─ HTTPS/TLS 1.3 everywhere                             │
├─────────────────────────────────────────────────────────────┤
│  🛡️ Layer 2: XSS Protection                                 │
│     └─ CSP, Trusted Types, HTML sanitization                │
├─────────────────────────────────────────────────────────────┤
│  🔐 Layer 1: Client-Side Encryption                         │
│     └─ AES-256-GCM, PBKDF2 key derivation                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Backend Infrastructure

### AWS Services Used

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **API Gateway** | REST API endpoint | Regional, API Key auth |
| **Lambda** | Serverless compute | Python 3.11, 256MB RAM |
| **DynamoDB** | NoSQL database | On-demand capacity, TTL enabled |
| **CloudWatch** | Logging & monitoring | Log retention: 30 days |

### Lambda Handler Structure

```python
def handler(event, context):
    path = event.get('path', '')
    method = event.get('httpMethod', '')
    
    if path == '/auth/register' and method == 'POST':
        return handle_register(event)
    elif path == '/auth/login' and method == 'POST':
        return handle_login(event)
    elif path == '/chat' and method == 'POST':
        return handle_chat(event)
    elif path == '/summaries' and method == 'GET':
        return handle_get_summaries(event)
    else:
        return error_response('Not found', 404)
```

### DynamoDB Tables

**ChatHistory:**
```
Primary Key: session_id (String)
Sort Key: timestamp (Number)
Attributes: role, content, username
TTL: ttl (30 days from creation)
```

**Users:**
```
Primary Key: username (String)
Attributes: password_hash (Binary)
```

**ChatSummaries:**
```
Primary Key: username (String)
Sort Key: session_id (String)
Attributes: summary, created_at
TTL: ttl (30 days from creation)
```

---

## Frontend Implementation

### Technology Stack

| Component | Technology |
|-----------|------------|
| HTML/CSS | Vanilla (no framework) |
| JavaScript | ES6 modules |
| Styling | CSS custom properties |
| Fonts | Cormorant Garamond, Inter |
| Icons | Inline SVG |

### File Structure

```
web/
├── index.html          # Main application
├── vercel.json         # Deployment config
├── netlify.toml        # Alt deployment config
└── js/
    ├── config.js       # API configuration
    ├── app.js          # Main application logic
    ├── encryption.js   # Client-side encryption
    ├── sanitize.js     # HTML sanitization
    └── dom-utils.js    # Trusted Types utilities
```

### Features

| Feature | Implementation |
|---------|---------------|
| **Voice Input** | Web Speech API (SpeechRecognition) |
| **Voice Output** | Web Speech API (SpeechSynthesis) |
| **Dark Mode** | CSS custom properties + localStorage |
| **Responsive** | CSS media queries (768px, 375px breakpoints) |
| **Mobile Menu** | JavaScript toggle for sidebar |

### Voice Implementation

```javascript
// Speech Recognition
const recognition = new webkitSpeechRecognition();
recognition.continuous = false;
recognition.interimResults = false;
recognition.lang = 'en-US';

recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    document.getElementById('chatInput').value = transcript;
};

// Speech Synthesis
function speakText(text) {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    speechSynthesis.speak(utterance);
}
```

---

## API Reference

### Base URL
```
https://pypwr35xf3.execute-api.us-east-1.amazonaws.com/prod
```

### Authentication
All requests require header:
```
x-api-key: <API_KEY>
```

### Endpoints

#### POST /auth/register
Register a new user.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "token": "base64_token"
}
```

---

#### POST /auth/login
Authenticate existing user.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "token": "base64_token",
  "username": "string"
}
```

---

#### POST /chat
Send a message and receive AI response.

**Request:**
```json
{
  "message": "string",
  "sessionId": "string (optional)",
  "token": "string"
}
```

**Response:**
```json
{
  "sessionId": "uuid",
  "response": "string",
  "options": ["string", "string"],
  "timestamp": 1234567890,
  "risk_level": "low|medium|high"
}
```

---

#### GET /summaries
Get user's conversation summaries.

**Query Parameters:**
- `token`: User authentication token

**Response:**
```json
{
  "summaries": [
    {
      "session_id": "uuid",
      "summary": "string",
      "created_at": 1234567890
    }
  ]
}
```

---

## Deployment

### Frontend (Vercel)

```bash
cd web
npx vercel --prod
```

**Live URL:** https://soulshield.vercel.app

### Backend (AWS CDK)

```bash
cd SoulShield
cdk deploy
```

### Environment Variables (Lambda)

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key |
| `LANGCHAIN_API_KEY` | LangSmith API key |
| `LANGCHAIN_PROJECT` | LangSmith project name |
| `LLM_PROVIDER` | `openai` or `bedrock` |
| `CHAT_TABLE_NAME` | DynamoDB chat table |
| `USERS_TABLE_NAME` | DynamoDB users table |
| `SUMMARIES_TABLE_NAME` | DynamoDB summaries table |

---

## Appendix: Prompt Templates

### Routing Agent Prompt

```
You are a safety-aware routing agent for a trauma-informed support system.

Analyze the user's message and classify it into:
1. MODE: "support" | "grounding" | "crisis"
2. PRIVACY_CONTEXT: "private" | "bystander_possible" | "bystander_present"
3. RISK_LEVEL: "low" | "medium" | "high"

Signals for bystander detection:
- "He might check my phone"
- "Someone could be watching"
- "I can't speak freely"
- "Need to be careful what I say"

Return ONLY valid JSON:
{"mode": "...", "privacy_context": "...", "risk_level": "..."}
```

### Support Coach Prompt

```
You are a trauma-informed support companion. 

CURRENT CONTEXT:
- Mode: {mode}
- Privacy: {privacy_context}

IF privacy_context is NOT "private":
- Use neutral, everyday language
- NEVER use: abuse, escape, police, violence, trafficking, danger
- Sound like a generic wellness app

ALWAYS:
- Reflect the user's words back
- Offer choices, never commands
- Be warm but not overly effusive
- Keep responses concise (2-3 sentences)

Return JSON: {"response_text": "...", "options": [...]}
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Dec 2024 | Initial release |
| 1.1.0 | Dec 2024 | Added dark mode, crisis resources |
| 1.2.0 | Dec 2024 | Mobile responsive design |

---

*SoulShield - Support that hides in plain sight.*

