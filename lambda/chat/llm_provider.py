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
    format_vars['user_message'] = user_message
    
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


def validate_coach_response(response: Dict) -> bool:
    """
    Validate the support_coach response.
    
    Rules:
    - JSON parses correctly (already done by caller)
    - options length <= 3
    - response_text is not empty
    """
    if not isinstance(response, dict):
        return False
    
    response_text = response.get('response_text', '')
    if not response_text or not isinstance(response_text, str):
        return False
    
    options = response.get('options', [])
    if not isinstance(options, list) or len(options) > 3:
        return False
    
    return True


def run_chat_pipeline(user_message: str, conversation_history: List[Dict]) -> Dict:
    """
    Execute the chat pipeline:
    1. Call routing_agent_prompt to determine mode
    2. Call support_coach with mode to generate response
    3. Validate response
    4. If validation fails, call safety_fallback
    5. Return only response_text and options
    
    Args:
        user_message: The current user message
        conversation_history: Previous conversation messages
    
    Returns:
        Dict with 'response_text' and 'options' keys only
    """
    try:
        # Step 1: Call routing_agent_prompt to get mode
        routing_result = call_openai_with_prompt(
            prompt_name='routing_agent_prompt',
            user_message=user_message,
            variables={'conversation_history': json.dumps(conversation_history[-10:])}
        )
        mode = routing_result.get('mode', 'general')
        print(f"Routing determined mode: {mode}")
        
        # Step 2: Call support_coach with the mode
        coach_response = call_openai_with_prompt(
            prompt_name='support_coach',
            user_message=user_message,
            variables={
                'mode': mode,
                'conversation_history': json.dumps(conversation_history[-10:])
            }
        )
        
        # Step 3: Validate the response
        if validate_coach_response(coach_response):
            # Step 5: Return only response_text and options
            return {
                'response_text': coach_response.get('response_text', ''),
                'options': coach_response.get('options', [])
            }
        
        print("Validation failed, calling safety_fallback")
        
    except Exception as e:
        print(f"Pipeline error, calling safety_fallback: {str(e)}")
    
    # Step 4: Call safety_fallback if validation fails or error occurred
    try:
        fallback_response = call_openai_with_prompt(
            prompt_name='safety_fallback',
            user_message=user_message,
            variables={}
        )
        
        return {
            'response_text': fallback_response.get('response_text', "I'm here to help. Could you tell me more about what you need?"),
            'options': fallback_response.get('options', [])
        }
    except Exception as e:
        print(f"Safety fallback also failed: {str(e)}")
        # Ultimate fallback
        return {
            'response_text': "I'm here to help. Could you please rephrase your question?",
            'options': []
        }


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
