#!/bin/bash

curl -X POST http://localhost:3000/ask -H "Content-Type: application/json" -d '{"question": "What is the capital of California?"}'
