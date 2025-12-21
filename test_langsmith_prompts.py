#!/usr/bin/env python3
"""
Test LangSmith prompts directly - NO AWS required.
Run: python test_langsmith_prompts.py
"""
import os
import sys
import json
from dotenv import load_dotenv

load_dotenv()

# Check required env vars
required = {
    'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
    'LANGCHAIN_API_KEY': os.getenv('LANGCHAIN_API_KEY'),
}

missing = [k for k, v in required.items() if not v or 'your-' in str(v).lower()]
if missing:
    print("❌ Missing or placeholder values in .env:")
    for var in missing:
        print(f"   {var}")
    print("\n📝 Edit your .env file and add real values:")
    print("   OPENAI_API_KEY=sk-...")
    print("   LANGCHAIN_API_KEY=lsv2_...")
    print("   LANGCHAIN_TRACING_V2=true")
    print("   LANGCHAIN_PROJECT=SoulShield")
    print("   LLM_PROVIDER=openai")
    print("   OPENAI_MODEL=gpt-4o-mini")
    sys.exit(1)

from langsmith import Client
from openai import OpenAI

OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')


def test_prompt(prompt_name: str, variables: dict) -> dict:
    """Pull a LangSmith prompt and call OpenAI with it."""
    print(f"\n{'='*50}")
    print(f"📋 Testing: {prompt_name}")
    print(f"{'='*50}")
    
    # Pull prompt from LangSmith
    ls_client = Client()
    
    try:
        prompt = ls_client.pull_prompt(prompt_name)
        print(f"✅ Prompt pulled successfully")
    except Exception as e:
        print(f"❌ Failed to pull prompt: {e}")
        return {}
    
    # Format the prompt
    try:
        formatted = prompt.invoke(variables)
        messages = []
        for msg in formatted.to_messages():
            role = 'user' if msg.type == 'human' else msg.type
            messages.append({'role': role, 'content': msg.content})
        print(f"✅ Prompt formatted with variables: {list(variables.keys())}")
    except Exception as e:
        print(f"❌ Failed to format prompt: {e}")
        return {}
    
    # Call OpenAI
    try:
        client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            response_format={"type": "json_object"},
            max_tokens=1024
        )
        content = response.choices[0].message.content or '{}'
        result = json.loads(content)
        print(f"✅ OpenAI response received")
        print(f"📤 Result: {json.dumps(result, indent=2)}")
        return result
    except Exception as e:
        print(f"❌ OpenAI call failed: {e}")
        return {}


def main():
    print("\n🧪 LangSmith Prompt Tester (No AWS Required)")
    print("=" * 50)
    
    test_question = "I'm feeling stressed about work lately"
    
    # Test 1: routing_agent_prompt
    routing_result = test_prompt(
        'routing_agent_prompt',
        {'question': test_question, 'conversation_history': '[]'}
    )
    mode = routing_result.get('mode', 'general')
    
    # Test 2: support_coach
    coach_result = test_prompt(
        'support_coach',
        {
            'question': test_question,
            'mode': mode,
            'conversation_history': '[]'
        }
    )
    
    # Validate coach response
    print(f"\n{'='*50}")
    print("🔍 Validating support_coach response")
    print("=" * 50)
    
    # Normalize response (handle nested format)
    def normalize(resp):
        if 'response' in resp and isinstance(resp['response'], dict):
            inner = resp['response']
            text = inner.get('message') or inner.get('reflection') or inner.get('response_text') or ''
            return {
                'response_text': text,
                'options': inner.get('options', [])
            }
        text = resp.get('response_text') or resp.get('message') or resp.get('reflection') or ''
        return {
            'response_text': text,
            'options': resp.get('options', [])
        }
    
    normalized = normalize(coach_result)
    response_text = normalized.get('response_text', '')
    options = normalized.get('options', [])
    
    valid = True
    if not response_text:
        print("❌ response_text is empty")
        valid = False
    else:
        print(f"✅ response_text: {response_text[:100]}...")
    
    if not isinstance(options, list):
        print("❌ options is not a list")
        valid = False
    elif len(options) > 3:
        print(f"❌ options has {len(options)} items (max 3)")
        valid = False
    else:
        print(f"✅ options ({len(options)}): {options}")
    
    # Test 3: safety_fallback
    fallback_result = test_prompt(
        'safety_fallback',
        {'question': test_question}
    )
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 SUMMARY")
    print("=" * 50)
    print(f"routing_agent_prompt: {'✅ OK' if routing_result else '❌ FAILED'}")
    print(f"support_coach: {'✅ OK' if coach_result else '❌ FAILED'}")
    print(f"safety_fallback: {'✅ OK' if fallback_result else '❌ FAILED'}")
    print(f"Validation: {'✅ PASSED' if valid else '❌ FAILED'}")
    print("\n🔗 Check traces at: https://smith.langchain.com")


if __name__ == "__main__":
    main()

