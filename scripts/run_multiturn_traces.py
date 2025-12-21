#!/usr/bin/env python3
"""
Multi-Turn Conversation Trace Runner for SoulShield

Runs multi-turn conversation scenarios and logs traces to LangSmith
with metadata for analysis.

Usage:
    cd SoulShield
    source venv/bin/activate
    python scripts/run_multiturn_traces.py

Or with explicit env loading:
    export $(cat .env | xargs)
    PYTHONPATH=. python3 scripts/run_multiturn_traces.py
"""
import os
import sys
import json
import uuid
from typing import Dict, List

# Add lambda/chat to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lambda', 'chat'))

from dotenv import load_dotenv
load_dotenv()

# Verify required env vars
required_vars = ['OPENAI_API_KEY', 'LANGCHAIN_API_KEY']
missing = [v for v in required_vars if not os.getenv(v)]
if missing:
    print(f"❌ Missing environment variables: {missing}")
    sys.exit(1)

from langsmith import traceable
from llm_provider import call_openai_with_prompt, extract_text_from_response, extract_options_from_response


def load_scenarios(path: str = None) -> List[Dict]:
    """Load multi-turn scenarios from JSON file."""
    if path is None:
        path = os.path.join(os.path.dirname(__file__), 'multiturn_scenarios.json')
    
    with open(path, 'r') as f:
        return json.load(f)


@traceable(run_type="chain", name="multiturn_pipeline")
def run_pipeline_turn(
    user_message: str,
    conversation_history: List[Dict],
    metadata: Dict
) -> Dict:
    """
    Run a single turn of the pipeline with routing.
    Decorated with @traceable for LangSmith tracing.
    """
    predicted_mode = "unknown"
    used_fallback = False
    response_text = ""
    options = []
    
    try:
        # Step 1: Call routing_agent_prompt to get mode
        routing_result = call_openai_with_prompt(
            prompt_name='routing_agent_prompt',
            user_message=user_message,
            variables={'conversation_history': json.dumps(conversation_history[-6:])}
        )
        predicted_mode = routing_result.get('mode', 'unknown')
        
        # Step 2: Call support_coach with the mode
        coach_response = call_openai_with_prompt(
            prompt_name='support_coach',
            user_message=user_message,
            variables={
                'mode': predicted_mode,
                'conversation_history': json.dumps(conversation_history[-6:])
            }
        )
        
        # Extract response
        response_text = extract_text_from_response(coach_response)
        options = extract_options_from_response(coach_response)
        
        if not response_text:
            used_fallback = True
        
    except Exception as e:
        print(f"    ⚠ Error: {str(e)[:40]}")
        used_fallback = True
    
    # Call safety_fallback if needed
    if used_fallback:
        try:
            fallback_response = call_openai_with_prompt(
                prompt_name='safety_fallback',
                user_message=user_message,
                variables={}
            )
            response_text = extract_text_from_response(fallback_response) or "I'm here to help."
            options = extract_options_from_response(fallback_response)
        except:
            response_text = "I'm here to help."
            options = []
    
    return {
        'predicted_mode': predicted_mode,
        'response_text': response_text,
        'options': options,
        'used_fallback': used_fallback,
        'metadata': metadata
    }


@traceable(run_type="chain", name="multiturn_conversation")
def run_conversation(scenario: Dict, conversation_id: str) -> List[Dict]:
    """
    Run a full multi-turn conversation for a scenario.
    """
    scenario_name = scenario.get('scenario', 'unknown')
    turns = scenario.get('turns', [])
    
    conversation_history = []
    results = []
    
    for turn_index, user_message in enumerate(turns):
        # Build metadata for this turn
        metadata = {
            'conversation_id': conversation_id,
            'scenario': scenario_name,
            'turn_index': turn_index,
            'run_type': 'multiturn_eval'
        }
        
        # Run the pipeline for this turn
        result = run_pipeline_turn(
            user_message=user_message,
            conversation_history=conversation_history,
            metadata=metadata
        )
        
        # Update conversation history
        conversation_history.append({
            'role': 'user',
            'content': user_message
        })
        conversation_history.append({
            'role': 'assistant',
            'content': result['response_text']
        })
        
        results.append({
            'turn_index': turn_index,
            'user_message': user_message,
            'response_text': result['response_text'],
            'options': result['options'],
            'predicted_mode': result['predicted_mode'],
            'used_fallback': result['used_fallback']
        })
    
    return results


def run_all_scenarios():
    """Run all scenarios and print results."""
    print("=" * 70)
    print("🔄 SoulShield Multi-Turn Conversation Traces")
    print("=" * 70)
    
    # Load scenarios
    scenarios = load_scenarios()
    print(f"\n📋 Loaded {len(scenarios)} scenarios\n")
    
    for scenario in scenarios:
        scenario_name = scenario.get('scenario', 'unknown')
        conversation_id = str(uuid.uuid4())
        
        print("-" * 70)
        print(f"🎭 Scenario: {scenario_name}")
        print(f"   Conversation ID: {conversation_id[:8]}...")
        print("-" * 70)
        
        # Run the conversation
        results = run_conversation(scenario, conversation_id)
        
        # Print each turn
        for r in results:
            print(f"\n  [{r['turn_index'] + 1}] 👤 User: {r['user_message']}")
            print(f"      🤖 Assistant: {r['response_text'][:100]}{'...' if len(r['response_text']) > 100 else ''}")
            if r['options']:
                print(f"      📌 Options: {r['options']}")
            print(f"      🏷️  Mode: {r['predicted_mode']}" + (" (fallback)" if r['used_fallback'] else ""))
        
        print()
    
    print("=" * 70)
    print("✅ All scenarios completed!")
    print("🔗 View traces at: https://smith.langchain.com")
    print("   Filter by: run_type = 'multiturn_eval'")
    print("=" * 70)


if __name__ == "__main__":
    run_all_scenarios()

