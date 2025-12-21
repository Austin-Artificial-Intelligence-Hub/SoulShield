#!/usr/bin/env python3
"""
Local test script for the LangSmith routing pipeline.
Run: python test_pipeline.py
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Verify required env vars
required_vars = ['OPENAI_API_KEY', 'LANGCHAIN_API_KEY']
missing = [v for v in required_vars if not os.getenv(v)]
if missing:
    print(f"❌ Missing environment variables: {missing}")
    print("Create a .env file with:")
    print("  OPENAI_API_KEY=sk-...")
    print("  OPENAI_MODEL=gpt-4o-mini")
    print("  LANGCHAIN_TRACING_V2=true")
    print("  LANGCHAIN_API_KEY=lsv2_...")
    print("  LANGCHAIN_PROJECT=SoulShield")
    sys.exit(1)

# Add lambda/chat to path so we can import llm_provider
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lambda', 'chat'))

# Set required env vars for llm_provider
os.environ.setdefault('OPENAI_MODEL', 'gpt-4o-mini')

from llm_provider import run_chat_pipeline

def test_pipeline():
    print("=" * 50)
    print("🧪 Testing LangSmith Routing Pipeline")
    print("=" * 50)
    
    test_messages = [
        "Hello, I need some help",
        "I'm feeling really stressed about work",
        "What's the weather like today?",
        "Can you explain how photosynthesis works?",
    ]
    
    conversation_history = []
    
    for msg in test_messages:
        print(f"\n📤 User: {msg}")
        print("-" * 40)
        
        try:
            result = run_chat_pipeline(msg, conversation_history)
            print(f"📥 Response: {result.get('response_text', 'No response')}")
            if result.get('options'):
                print(f"   Options: {result.get('options')}")
            
            # Add to history for next iteration
            conversation_history.append({'role': 'user', 'content': msg})
            conversation_history.append({'role': 'assistant', 'content': result.get('response_text', '')})
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 50)
    print("✅ Pipeline test complete!")
    print("Check LangSmith for traces: https://smith.langchain.com")
    print("=" * 50)

if __name__ == "__main__":
    test_pipeline()

