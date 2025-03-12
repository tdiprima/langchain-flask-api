#!/bin/bash
# Description: Example cURL requests
# Author: tdiprima

# Step 1: Start a New Conversation
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the capital of California?"}'

# Step2: Continue the Conversation
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is its population?",
    "session_id": "123e4567-e89b-12d3-a456-426614174000"
  }'

# Step 3: Start a new conversation
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "question": "Tell me a joke.",
    "new_conversation": true
  }'
