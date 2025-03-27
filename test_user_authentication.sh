#!/bin/bash
# Adds logins

echo "Starting Flask app (run this separately: python user_authentication.py)"
echo "Testing user authentication..."

# Register a new user
echo "Registering testuser..."
curl -X POST http://localhost:3000/register -H "Content-Type: application/json" -d '{"username": "testuser", "password": "password123"}'

# Log in
echo "Logging in testuser..."
curl -X POST http://localhost:3000/login -H "Content-Type: application/json" -d '{"username": "testuser", "password": "password123"}'

# Ask a question (replace YOUR_SESSION_ID)
echo "Asking a question with session ID..."
curl -X POST http://localhost:3000/ask -H "Content-Type: application/json" -d '{"question": "What is machine learning?", "session_id": "YOUR_SESSION_ID"}'

# Log out
echo "Logging out..."
curl -X POST http://localhost:3000/logout -H "Content-Type: application/json" -d '{"session_id": "YOUR_SESSION_ID"}'
