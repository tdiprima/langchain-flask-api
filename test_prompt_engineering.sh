#!/bin/bash
# Spices up responses with personas

echo "Starting Flask app (run this separately: python prompt_engineering.py)"
echo "Testing advanced prompt engineering..."

# List personas
echo "Listing available personas..."
curl -X GET http://localhost:3000/personas

# Ask a factual question with expert persona
echo "Asking a factual question with expert persona..."
curl -X POST http://localhost:3000/ask -H "Content-Type: application/json" -d '{"question": "What is quantum computing?", "persona": "expert"}'

# Ask an opinion question with friendly persona
echo "Asking an opinion question with friendly persona..."
curl -X POST http://localhost:3000/ask -H "Content-Type: application/json" -d '{"question": "What do you think about artificial intelligence?", "persona": "friendly"}'

# Ask an instruction question with concise persona
echo "Asking an instruction question with concise persona..."
curl -X POST http://localhost:3000/ask -H "Content-Type: application/json" -d '{"question": "How do I learn programming?", "persona": "concise"}'
