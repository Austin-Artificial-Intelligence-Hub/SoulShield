#!/usr/bin/env python3
"""
LangSmith Experiment Runner for SoulShield Pipeline

Runs the existing pipeline against a LangSmith dataset and logs results
to LangSmith for visualization in the UI.

Usage:
    python scripts/run_langsmith_experiment.py
"""
import os
import sys
import json
from datetime import datetime
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

from langsmith import Client, evaluate
from llm_provider import call_openai_with_prompt, extract_text_from_response, extract_options_from_response

# Dataset configuration
DATASET_NAME = "soulshield_dataset"


def run_pipeline_with_routing(inputs: Dict) -> Dict:
    """
    Target function for LangSmith evaluate().
    Runs the full pipeline and returns outputs.
    """
    user_message = inputs.get('user_message', inputs.get('question', ''))
    
    predicted_mode = "unknown"
    used_fallback = False
    response_text = ""
    options = []
    
    try:
        # Step 1: Call routing_agent_prompt to get mode
        routing_result = call_openai_with_prompt(
            prompt_name='routing_agent_prompt',
            user_message=user_message,
            variables={'conversation_history': '[]'}
        )
        predicted_mode = routing_result.get('mode', 'unknown')
        
        # Step 2: Call support_coach with the mode
        coach_response = call_openai_with_prompt(
            prompt_name='support_coach',
            user_message=user_message,
            variables={
                'mode': predicted_mode,
                'conversation_history': '[]'
            }
        )
        
        # Extract response
        response_text = extract_text_from_response(coach_response)
        options = extract_options_from_response(coach_response)
        
        if not response_text:
            used_fallback = True
        
    except Exception as e:
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
        'used_fallback': used_fallback
    }


def routing_accuracy_evaluator(run, example) -> Dict:
    """Evaluator: Check if predicted mode matches expected mode."""
    predicted = run.outputs.get('predicted_mode', 'unknown').lower()
    expected = example.outputs.get('expected_mode', 'unknown').lower()
    
    return {
        'key': 'routing_accuracy',
        'score': 1.0 if predicted == expected else 0.0,
        'comment': f"Expected: {expected}, Got: {predicted}"
    }


def fallback_rate_evaluator(run, example) -> Dict:
    """Evaluator: Track if fallback was used."""
    used_fallback = run.outputs.get('used_fallback', False)
    
    return {
        'key': 'used_fallback',
        'score': 0.0 if used_fallback else 1.0,  # 1 = good (no fallback), 0 = fallback used
        'comment': "Fallback was used" if used_fallback else "No fallback needed"
    }


def has_response_evaluator(run, example) -> Dict:
    """Evaluator: Check if response was generated."""
    response_text = run.outputs.get('response_text', '')
    has_response = bool(response_text and len(response_text) > 10)
    
    return {
        'key': 'has_response',
        'score': 1.0 if has_response else 0.0,
        'comment': f"Response length: {len(response_text)}"
    }


def run_experiment():
    """Run the experiment using LangSmith evaluate()."""
    print("=" * 60)
    print("🧪 SoulShield Pipeline Experiment")
    print("=" * 60)
    
    experiment_name = f"soulshield-eval-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    print(f"\n📊 Dataset: {DATASET_NAME}")
    print(f"🔬 Experiment: {experiment_name}\n")
    
    # Run evaluation with LangSmith
    results = evaluate(
        run_pipeline_with_routing,
        data=DATASET_NAME,
        evaluators=[
            routing_accuracy_evaluator,
            fallback_rate_evaluator,
            has_response_evaluator,
        ],
        experiment_prefix=experiment_name,
    )
    
    # Collect metrics from results
    routing_scores = []
    fallback_scores = []
    
    for result in results:
        eval_results = result.get('evaluation_results', {})
        if 'results' in eval_results:
            for er in eval_results['results']:
                if er.key == 'routing_accuracy':
                    routing_scores.append(er.score)
                elif er.key == 'used_fallback':
                    fallback_scores.append(1 - er.score)  # Invert: 1 = used fallback
    
    # Print summary
    total = len(routing_scores)
    if total > 0:
        routing_accuracy = (sum(routing_scores) / total) * 100
        fallback_rate = (sum(fallback_scores) / total) * 100
        
        print("\n" + "=" * 60)
        print("📈 RESULTS")
        print("=" * 60)
        print(f"\n{'Metric':<25} {'Value':>15}")
        print("-" * 40)
        print(f"{'Total Examples':<25} {total:>15}")
        print(f"{'Routing Accuracy':<25} {routing_accuracy:>14.1f}%")
        print(f"{'Fallback Rate':<25} {fallback_rate:>14.1f}%")
    
    print("\n" + "=" * 60)
    print("🔗 View experiment in LangSmith:")
    print(f"   https://smith.langchain.com")
    print(f"   → Datasets → {DATASET_NAME} → Experiments")
    print("=" * 60)


if __name__ == "__main__":
    run_experiment()

