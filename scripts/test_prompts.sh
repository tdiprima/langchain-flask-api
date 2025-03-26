#!/bin/bash

# Start your Flask app (uncomment if not already running)
# export OPENAI_API_VERSION="2023-05-15" && python app.py

# 2. List available personas - see what flavors your chatbot's got!
echo "Fetching available personas..."
curl -X GET http://localhost:3000/personas

# 3. Ask a factual question with the expert persona - get that brainy vibe
echo -e "\nAsking a factual question with expert persona..."
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What is quantum computing?", "persona":"expert"}'

# 4. Ask an opinion question with the friendly persona - chill and chatty
echo -e "\nAsking an opinion question with friendly persona..."
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"What do you think about artificial intelligence?", "persona":"friendly"}'

# 5. Ask an instruction question with the concise persona - short and sweet
echo -e "\nAsking an instruction question with concise persona..."
curl -X POST http://localhost:3000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"How do I learn programming?", "persona":"concise"}'

echo -e "\nDone testing! Check the responses above. 🚀"
