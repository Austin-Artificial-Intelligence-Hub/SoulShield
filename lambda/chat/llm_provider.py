import os
import json
import boto3
from typing import List, Dict

LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'bedrock')


def call_llm(messages: List[Dict]) -> str:
    """Call LLM provider based on configuration"""
    if LLM_PROVIDER == 'openai':
        return call_openai(messages)
    else:
        return call_bedrock(messages)


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
