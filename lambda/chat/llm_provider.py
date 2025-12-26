import os
import json
import boto3
from typing import List, Dict, Optional

LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'bedrock')
OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
BEDROCK_MODEL = os.environ.get('BEDROCK_MODEL', 'anthropic.claude-3-haiku-20240307-v1:0')

# Supported models configuration
SUPPORTED_OPENAI_MODELS = ['gpt-4o-mini', 'gpt-4o', 'gpt-4-turbo', 'gpt-3.5-turbo']
SUPPORTED_BEDROCK_MODELS = [
    'anthropic.claude-3-haiku-20240307-v1:0',
    'anthropic.claude-3-sonnet-20240229-v1:0',
    'anthropic.claude-3-opus-20240229-v1:0',
    'anthropic.claude-3-5-sonnet-20240620-v1:0'
]

# LangSmith tracing is auto-enabled via environment variables:
# LANGCHAIN_TRACING_V2, LANGCHAIN_API_KEY, LANGCHAIN_PROJECT


def call_llm(messages: List[Dict], model: Optional[str] = None, provider: Optional[str] = None) -> str:
    """
    Call LLM provider based on configuration
    
    Args:
        messages: List of message dictionaries
        model: Optional model name to override default (e.g., 'gpt-4o', 'claude-3-sonnet')
        provider: Optional provider to override default ('openai' or 'bedrock')
    
    Returns:
        Generated text response
    """
    # Determine provider
    selected_provider = provider or LLM_PROVIDER
    
    if selected_provider == 'openai':
        selected_model = model or OPENAI_MODEL
        return call_openai(messages, model=selected_model)
    else:
        selected_model = model or BEDROCK_MODEL
        return call_bedrock(messages, model=selected_model)


def call_openai_with_prompt(prompt_name: str, user_message: str, variables: Optional[Dict] = None, model: Optional[str] = None) -> Dict:
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
    
    # Use provided model or default
    selected_model = model or OPENAI_MODEL
    
    response = client.chat.completions.create(
        model=selected_model,
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


def run_routing_agent(user_message: str, conversation_history: List[Dict]) -> Dict:
    """
    Step 1: Run the routing agent to classify the message.
    
    Args:
        user_message: The user's current message
        conversation_history: Previous conversation messages
    
    Returns:
        Dict with 'mode', 'privacy_context', 'risk_level' keys
        Defaults to safe values if routing fails
    """
    try:
        routing_result = call_openai_with_prompt(
            prompt_name='routing_agent_prompt',
            user_message=user_message,
            variables={
                'conversation_history': json.dumps(conversation_history[-6:])
            }
        )
        
        # Normalize keys (handle uppercase from some responses)
        normalized = {}
        for key, value in routing_result.items():
            normalized[key.lower()] = value
        
        # Validate and extract routing decision
        mode = normalized.get('mode', 'normal_support')
        privacy_context = normalized.get('privacy_context', 'unknown')
        risk_level = normalized.get('risk_level', 'low')
        
        # Validate mode
        valid_modes = ['normal_support', 'grounding', 'therapy_prep', 'crisis_resources']
        if mode not in valid_modes:
            mode = 'normal_support'
        
        # Validate privacy_context
        valid_privacy = ['unknown', 'private', 'bystander_possible']
        if privacy_context not in valid_privacy:
            privacy_context = 'unknown'
        
        # Validate risk_level
        valid_risk = ['low', 'medium', 'high']
        if risk_level not in valid_risk:
            risk_level = 'low'
        
        print(f"Routing result: mode={mode}, privacy={privacy_context}, risk={risk_level}")
        
        return {
            'mode': mode,
            'privacy_context': privacy_context,
            'risk_level': risk_level
        }
        
    except Exception as e:
        print(f"Routing agent error: {str(e)}, using defaults")
        return {
            'mode': 'normal_support',
            'privacy_context': 'unknown',
            'risk_level': 'low'
        }


def run_support_coach(user_message: str, conversation_history: List[Dict], 
                       mode: str, privacy_context: str) -> Dict:
    """
    Step 2: Run the support coach with the routed mode.
    
    Args:
        user_message: The user's current message
        conversation_history: Previous conversation messages
        mode: The routing mode (normal_support, grounding, therapy_prep, crisis_resources)
        privacy_context: Privacy context (unknown, private, bystander_possible)
    
    Returns:
        Dict with 'response_text' and 'options' keys
    """
    try:
        # Include recent conversation history
        history_context = json.dumps(conversation_history[-6:]) if conversation_history else "[]"
        
        # Include privacy context in mode description for the coach
        mode_with_privacy = f"{mode} (privacy_context: {privacy_context})"
        
        coach_response = call_openai_with_prompt(
            prompt_name='support_coach',
            user_message=user_message,
            variables={
                'mode': mode_with_privacy,
                'conversation_history': history_context
            }
        )
        
        # Extract response
        text = extract_text_from_response(coach_response)
        options = extract_options_from_response(coach_response)
        
        if text:
            return {
                'response_text': text,
                'options': options
            }
        
        print("Support coach returned no text")
        return None
        
    except Exception as e:
        print(f"Support coach error: {str(e)}")
        return None


def run_safety_fallback(user_message: str) -> Dict:
    """
    Step 3 (fallback): Run safety fallback when other agents fail.
    
    Args:
        user_message: The user's current message
    
    Returns:
        Dict with 'response_text' and 'options' keys
    """
    try:
        fallback_response = call_openai_with_prompt(
            prompt_name='safety_fallback',
            user_message=user_message,
            variables={}
        )
        
        text = extract_text_from_response(fallback_response)
        options = extract_options_from_response(fallback_response)
        
        return {
            'response_text': text or "I'm here to help. Could you tell me more?",
            'options': options
        }
        
    except Exception as e:
        print(f"Safety fallback error: {str(e)}")
        return {
            'response_text': "I'm here to support you. Take your time.",
            'options': []
        }


def run_chat_pipeline(user_message: str, conversation_history: List[Dict]) -> Dict:
    """
    Agentic pipeline:
    1. routing_agent_prompt → Classify message (mode, privacy, risk)
    2. support_coach → Generate response based on routing
    3. safety_fallback → If coach fails, provide safe fallback
    
    Args:
        user_message: The current user message
        conversation_history: Previous conversation messages
    
    Returns:
        Dict with 'response_text', 'options', and 'routing' keys
    """
    result = {
        'response_text': '',
        'options': [],
        'routing': None
    }
    
    try:
        # Step 1: Run routing agent to classify the message
        print(f"Routing: '{user_message[:50]}...'")
        routing = run_routing_agent(user_message, conversation_history)
        result['routing'] = routing
        
        # Step 2: Run support coach with routed mode
        print(f"Coach: mode={routing['mode']}, privacy={routing['privacy_context']}")
        coach_result = run_support_coach(
            user_message=user_message,
            conversation_history=conversation_history,
            mode=routing['mode'],
            privacy_context=routing['privacy_context']
        )
        
        if coach_result and coach_result.get('response_text'):
            result['response_text'] = coach_result['response_text']
            result['options'] = coach_result.get('options', [])
            return result
        
        print("Coach failed, running safety fallback")
        
    except Exception as e:
        print(f"Pipeline error: {str(e)}, running safety fallback")
    
    # Step 3: Safety fallback if routing or coach failed
    fallback_result = run_safety_fallback(user_message)
    result['response_text'] = fallback_result['response_text']
    result['options'] = fallback_result.get('options', [])
    
    return result


def call_bedrock(messages: List[Dict], model: Optional[str] = None) -> str:
    """
    Call AWS Bedrock with Claude
    
    Args:
        messages: List of message dictionaries
        model: Optional model ID to override default
    """
    client = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

    # Use provided model or default
    model_id = model or BEDROCK_MODEL
    
    # Validate model is in supported list
    if model_id not in SUPPORTED_BEDROCK_MODELS:
        print(f"Warning: Model {model_id} not in supported list, using anyway")

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


def call_openai(messages: List[Dict], model: Optional[str] = None) -> str:
    """
    Call OpenAI API
    
    Args:
        messages: List of message dictionaries
        model: Optional model name to override default
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("OpenAI package not installed. Run: pip install openai")

    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
    
    # Use provided model or default
    selected_model = model or OPENAI_MODEL
    
    # Validate model is in supported list
    if selected_model not in SUPPORTED_OPENAI_MODELS:
        print(f"Warning: Model {selected_model} not in supported list, using anyway")

    response = client.chat.completions.create(
        model=selected_model,
        messages=messages,
        max_tokens=1024
    )

    return response.choices[0].message.content or 'No response generated'
