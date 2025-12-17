#!/usr/bin/env python3
"""
Test script for the chatbot API
Usage: python scripts/test_api.py <API_URL> <API_KEY>
"""

import sys
import json
import requests


def test_chatbot(api_url: str, api_key: str):
    """Test the chatbot API"""
    
    # Ensure URL ends with /
    if not api_url.endswith('/'):
        api_url += '/'
    
    endpoint = f"{api_url}chat"
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }
    
    print("Testing chatbot API...\n")
    
    # Test 1: Send initial message
    print("Test 1: Sending initial message...")
    payload = {
        'message': 'Hello! What can you help me with?'
    }
    
    response = requests.post(endpoint, headers=headers, json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2)}\n")
        
        session_id = data.get('sessionId')
        
        if session_id:
            # Test 2: Send follow-up message
            print("Test 2: Sending follow-up message with session...")
            payload = {
                'message': 'Can you remember what I just asked?',
                'sessionId': session_id
            }
            
            response = requests.post(endpoint, headers=headers, json=payload)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"Response: {json.dumps(data, indent=2)}")
            else:
                print(f"Error: {response.text}")
    else:
        print(f"Error: {response.text}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python scripts/test_api.py <API_URL> <API_KEY>")
        sys.exit(1)
    
    api_url = sys.argv[1]
    api_key = sys.argv[2]
    
    test_chatbot(api_url, api_key)
