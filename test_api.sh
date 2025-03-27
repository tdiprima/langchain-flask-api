#!/bin/bash
# Testing the API

# 1. Start the application (run this in a separate terminal)
# python app.py

# 2. Send a test question to the API
echo "Testing with question: 'What is the capital of California?'"
curl -X POST http://localhost:3000/ask -H "Content-Type: application/json" -d '{"question": "What is the capital of California?"}'
echo ""  # Newline for readability

# 3. Try another question
echo "Testing with another question: 'What is 2 + 2?'"
curl -X POST http://localhost:3000/ask -H "Content-Type: application/json" -d '{"question": "What is 2 + 2?"}'
echo ""  # Newline for readability
