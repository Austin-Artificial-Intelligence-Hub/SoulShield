import os
import json
import boto3
from typing import List, Dict, Optional

LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'bedrock')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')

# LangSmith tracing is auto-enabled via environment variables:
# LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT


def call_llm(messages: List[Dict]) -> str:
    """Call LLM provider based on configuration"""
    if LLM_PROVIDER == 'openai':
        return call_openai(messages)
    else:
        return call_bedrock(messages)


def call_openai_with_prompt(prompt_name: str, user_message: str, variables: Optional[Dict] = None) -> Dict:
    """
    Pull a prompt from LangSmith Hub and call OpenAI with structured JSON output.
    
    Args:
        prompt_name: Name of the LangSmith prompt (e.g., 'routing_agent_prompt')
        user_message: The user's message to include
        variables: Optional variables to format into the prompt template
    
    Returns:
        Parsed JSON response from the model
    """
    from langsmith import Client
    from openai import OpenAI
    
    # Pull prompt from LangSmith
    ls_client = Client()
    prompt = ls_client.pull_prompt(prompt_name)
    
    # Format the prompt with variables
    format_vars = variables or {}
    format_vars['question'] = user_message
    
    # Get the formatted messages from the prompt
    formatted = prompt.invoke(format_vars)
    
    # Convert to OpenAI message format
    messages = []
    for msg in formatted.to_messages():
        messages.append({
            'role': msg.type if msg.type != 'human' else 'user',
            'content': msg.content
        })
    
    # Call OpenAI with JSON response format
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        max_tokens=1024
    )
    
    content = response.choices[0].message.content or '{}'
    return json.loads(content)


def extract_text_from_response(response: Dict) -> str:
    """Extract text from any response structure - very lenient."""
    if not response:
        return ''
    
    # Known mode values to filter out (not actual responses)
    mode_values = {'normal_support', 'grounding', 'crisis_resources', 'therapy_prep', 'supportive', 'unknown'}
    
    def is_valid_text(text: str) -> bool:
        """Check if text is a valid response (not just a mode label)."""
        if not text or not isinstance(text, str):
            return False
        text_lower = text.strip().lower()
        if text_lower in mode_values:
            return False
        if len(text) < 15:  # Too short to be a real response
            return False
        return True
    
    # Try nested response.message/reflection
    if 'response' in response and isinstance(response['response'], dict):
        inner = response['response']
        text = inner.get('message') or inner.get('reflection') or inner.get('response_text') or inner.get('text') or ''
        if is_valid_text(text):
            return text
    
    # Try top-level fields
    for key in ['message', 'response_text', 'reflection', 'text', 'content', 'answer']:
        text = response.get(key)
        if is_valid_text(text):
            return text
    
    # Try any string value as last resort
    for value in response.values():
        if is_valid_text(value):
            return value
    
    return ''


def extract_options_from_response(response: Dict) -> list:
    """Extract options from any response structure."""
    if not response:
        return []
    
    # Try nested response.options
    if 'response' in response and isinstance(response['response'], dict):
        opts = response['response'].get('options', [])
        if isinstance(opts, list):
            return opts[:3]  # Max 3 options
    
    # Try top-level options
    opts = response.get('options', [])
    if isinstance(opts, list):
        return opts[:3]
    
    return []


def normalize_response(response: Dict) -> Dict:
    """Normalize response format from LangSmith prompts."""
    return {
        'response_text': extract_text_from_response(response),
        'options': extract_options_from_response(response),
        'suggest_human_support': False
    }


def validate_coach_response(response: Dict) -> bool:
    """Very lenient validation - just need some text."""
    text = extract_text_from_response(response)
    return bool(text and len(text) > 5)


def run_chat_pipeline(user_message: str, conversation_history: List[Dict], summary_context: str = "", skip_greeting: bool = False) -> Dict:
    """
    Simplified fast pipeline:
    1. Call support_coach directly (skip routing for speed)
    2. If that fails, call safety_fallback
    
    Args:
        user_message: The current user message
        conversation_history: Previous conversation messages
        summary_context: Optional summaries from past sessions for context
    
    Returns:
        Dict with 'response_text' and 'options' keys only
    """
    try:
        # Build context including past session summaries if available
        context_parts = []
        if summary_context:
            context_parts.append(summary_context)
        context_parts.append(json.dumps(conversation_history[-6:]))
        full_context = "\n".join(context_parts) if context_parts else "[]"
        
        # Build mode with skip_greeting instruction if needed
        mode = 'supportive'
        if skip_greeting:
            mode = 'supportive (NOTE: A personalized greeting was already shown to user. Do NOT greet or say hello again. Respond directly to their message.)'
        
        # Call support_coach directly with default mode (faster - 1 LLM call)
        coach_response = call_openai_with_prompt(
            prompt_name='support_coach',
            user_message=user_message,
            variables={
                'mode': mode,
                'conversation_history': full_context
            }
        )
        
        # Extract response (very lenient)
        text = extract_text_from_response(coach_response)
        if text:
            return {
                'response_text': text,
                'options': extract_options_from_response(coach_response)
            }
        
        print("No text in response, calling safety_fallback")
        
    except Exception as e:
        print(f"Pipeline error, calling safety_fallback: {str(e)}")
    
    # Fallback only if support_coach completely failed
    try:
        fallback_response = call_openai_with_prompt(
            prompt_name='safety_fallback',
            user_message=user_message,
            variables={}
        )
        
        text = extract_text_from_response(fallback_response)
        return {
            'response_text': text or "I'm here to help. Could you tell me more?",
            'options': extract_options_from_response(fallback_response)
        }
    except Exception as e:
        print(f"Safety fallback also failed: {str(e)}")
        return {
            'response_text': "I'm here to help. How can I assist you today?",
            'options': []
        }


def generate_session_greeting(summaries: List[Dict]) -> str:
    """
    Generate a personalized greeting based on past session summaries.
    Uses direct OpenAI call (not JSON format) for plain text greeting.
    
    Args:
        summaries: List of past session summaries [{summary: str, created_at: int}, ...]
    
    Returns:
        A personalized greeting/follow-up message
    """
    if not summaries:
        return "Welcome! I'm here to support you. How are you feeling today?"
    
    try:
        from openai import OpenAI
        
        # Build context from summaries
        summary_text = "\n".join([f"- {s['summary']}" for s in summaries[:3]])
        
        client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    'role': 'system',
                    'content': '''You are a warm, caring mental health support companion. 
Generate a brief, personalized greeting for a returning user based on their previous conversation summaries.

Guidelines:
- Keep it to 1-2 sentences
- Reference what they discussed before in a gentle, non-intrusive way
- Show you remember and care about their journey
- Ask a relevant follow-up question
- Be warm but not overly familiar

Examples:
- "Welcome back! Last time we worked on some grounding techniques for your anxiety. How have you been feeling since then?"
- "It's good to see you again. I remember you mentioned feeling overwhelmed. How are things going now?"
- "Hi there! We talked about some breathing exercises last time. Have you had a chance to try them?"'''
                },
                {
                    'role': 'user',
                    'content': f"Previous session summaries:\n{summary_text}\n\nGenerate a personalized greeting."
                }
            ],
            max_tokens=150
        )
        
        greeting = response.choices[0].message.content or ""
        return greeting.strip()
        
    except Exception as e:
        print(f"Error generating greeting: {str(e)}")
        return "Welcome back! I'm here to support you. How are you feeling today?"


def call_bedrock(messages: List[Dict]) -> str:
    """Call AWS Bedrock with Claude"""
    client = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

    # Using Claude 3 Haiku (cost-effective and fast)
    model_id = 'anthropic.claude-3-haiku-20240307-v1:0'

    # Separate system message from conversation
    system_message = next((m['content'] for m in messages if m['role'] == 'system'), None)
    conversation = [m for m in messages if m['role'] != 'system']

    payload = {
        'anthropic_version': 'bedrock-2023-05-31',
        'max_tokens': 1024,
        'messages': conversation,
    }

    if system_message:
        payload['system'] = system_message

    response = client.invoke_model(
        modelId=model_id,
        contentType='application/json',
        accept='application/json',
        body=json.dumps(payload)
    )

    response_body = json.loads(response['body'].read())
    return response_body['content'][0]['text']


def call_openai(messages: List[Dict]) -> str:
    """Call OpenAI API"""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")

    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

    response = client.chat.completions.create(
        model='gpt-4o-mini',
        messages=messages,
        max_tokens=1024
    )

    return response.choices[0].message.content or 'No response generated'
