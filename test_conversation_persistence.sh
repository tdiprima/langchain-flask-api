#!/bin/bash
# Keeps chats alive across restarts

echo "Starting Flask app (run this separately: python conversation_persistence.py)"
echo "Testing conversation persistence..."

# Generate a new session ID
echo "Generating new session ID..."
curl -X GET http://localhost:3000/generate-session

# Use session ID to ask questions (replace YOUR_SESSION_ID manually)
echo "Asking a question..."
curl -X POST http://localhost:3000/ask -H "Content-Type: application/json" -d '{"question": "What is artificial intelligence?", "session_id": "YOUR_SESSION_ID"}'

# Restart the app manually in another terminal, then:
echo "Verifying chat history after restart..."
curl -X GET "http://localhost:3000/history?session_id=YOUR_SESSION_ID"

# Ask a follow-up question
echo "Asking follow-up question..."
curl -X POST http://localhost:3000/ask -H "Content-Type: application/json" -d '{"question": "What are its main applications?", "session_id": "YOUR_SESSION_ID"}'
