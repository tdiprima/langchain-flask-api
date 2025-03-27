#!/bin/bash
# Testing the Multi-User Session Feature

# Test 1: Generate new session IDs for two different users
echo "Generating session ID for User 1..."
USER1_SESSION=$(curl -s -X GET http://localhost:3000/generate-session | jq -r '.session_id')
echo "User 1 session ID: $USER1_SESSION"

echo "Generating session ID for User 2..."
USER2_SESSION=$(curl -s -X GET http://localhost:3000/generate-session | jq -r '.session_id')
echo "User 2 session ID: $USER2_SESSION"
echo -e "\n"

# Test 2: Ask questions with different session IDs
echo "User 1 asks: What is the capital of France?"
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What is the capital of France?\", \"session_id\":\"$USER1_SESSION\"}"
echo -e "\n"

echo "User 2 asks: What is the largest planet in our solar system?"
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What is the largest planet in our solar system?\", \"session_id\":\"$USER2_SESSION\"}"
echo -e "\n"

# Test 3: Ask follow-up questions with different session IDs
echo "User 1 asks follow-up: What is its population?"
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What is its population?\", \"session_id\":\"$USER1_SESSION\"}"
echo -e "\n"

echo "User 2 asks follow-up: How many moons does it have?"
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"How many moons does it have?\", \"session_id\":\"$USER2_SESSION\"}"
echo -e "\n"

# Test 4: View chat histories for different sessions
echo "Viewing User 1's chat history..."
curl -X GET "http://localhost:3000/history?session_id=$USER1_SESSION"
echo -e "\n"

echo "Viewing User 2's chat history..."
curl -X GET "http://localhost:3000/history?session_id=$USER2_SESSION"
echo -e "\n"

# Test 5: List all active sessions
echo "Listing all active sessions..."
curl -X GET http://localhost:3000/sessions
echo -e "\n"

# Test 6: Clear chat history for a specific session (User 1)
echo "Clearing User 1's chat history..."
curl -X POST http://localhost:3000/clear-history \
  -H "Content-Type: application/json" \
  -d "{\"session_id\":\"$USER1_SESSION\"}"
echo -e "\n"

# Test 7: Clear all chat histories
echo "Clearing all chat histories..."
curl -X POST http://localhost:3000/clear-all-history
echo -e "\n"
