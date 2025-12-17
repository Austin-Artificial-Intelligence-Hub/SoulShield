#!/bin/bash

# Test script for the chatbot API
# Usage: ./scripts/test-api.sh <API_URL> <API_KEY>

API_URL=$1
API_KEY=$2

if [ -z "$API_URL" ] || [ -z "$API_KEY" ]; then
  echo "Usage: ./scripts/test-api.sh <API_URL> <API_KEY>"
  exit 1
fi

echo "Testing chatbot API..."
echo ""

# Test 1: Send a message
echo "Test 1: Sending a message..."
RESPONSE=$(curl -s -X POST "${API_URL}chat" \
  -H "Content-Type: application/json" \
  -H "x-api-key: ${API_KEY}" \
  -d '{
    "message": "Hello! What can you help me with?"
  }')

echo "Response: $RESPONSE"
echo ""

# Extract sessionId for follow-up
SESSION_ID=$(echo $RESPONSE | grep -o '"sessionId":"[^"]*"' | cut -d'"' -f4)

if [ -n "$SESSION_ID" ]; then
  echo "Test 2: Sending follow-up message with session..."
  curl -s -X POST "${API_URL}chat" \
    -H "Content-Type: application/json" \
    -H "x-api-key: ${API_KEY}" \
    -d "{
      \"message\": \"Can you remember what I just asked?\",
      \"sessionId\": \"${SESSION_ID}\"
    }" | jq '.'
fi
