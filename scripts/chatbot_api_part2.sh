#!/bin/bash
# Testing the Chat History Feature

# Test 1: Ask a question
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the capital of Mexico?"}'

# Test 2: Ask a follow-up question that references the previous question
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is its population?"}'

# Test 3: View the chat history
curl -X GET http://localhost:3000/history

# Test 4: Ask more questions to fill up the history
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What are some famous landmarks there?"}'

curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"Tell me about the cuisine in this city."}'

# Test 5: Clear the chat history
curl -X POST http://localhost:3000/clear-history \
  -H "Content-Type: application/json" \
  -d '{}'

# Test 6: Verify the history is cleared
curl -X GET http://localhost:3000/history
