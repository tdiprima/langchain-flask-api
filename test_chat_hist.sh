#!/bin/bash
# Testing the Chat History Feature

# Test 1: Ask a question - What's the capital of Mexico?
echo "Asking: What is the capital of Mexico?"
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is the capital of Mexico?"}'
echo -e "\n"

# Test 2: Follow-up question - What's its population?
echo "Asking follow-up: What is its population?"
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is its population?"}'
echo -e "\n"

# Test 3: Peek at the chat history
echo "Checking the chat history..."
curl -X GET http://localhost:3000/history
echo -e "\n"

# Test 4: Fill up the history with more questions
echo "Asking: What are some famous landmarks there?"
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What are some famous landmarks there?"}'
echo -e "\n"

#echo "Asking: Tell me about the cuisine in this city."
#curl -X POST http://localhost:3000/ask \
#  -H "Content-Type: application/json" \
#  -d '{"question":"Tell me about the cuisine in this city."}'
#echo -e "\n"

# Test 5: Wipe the slate clean
echo "Clearing the chat history..."
curl -X POST http://localhost:3000/clear-history \
  -H "Content-Type: application/json" \
  -d '{}'
echo -e "\n"

# Test 6: Double-check the history is gone
echo "Verifying the history is cleared..."
curl -X GET http://localhost:3000/history
echo -e "\n"
