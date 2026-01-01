#!/bin/bash
# Quick chatbot test script

echo "Testing chatbot with Phase 5 features..."
echo ""

# You need to replace YOUR_TOKEN with actual JWT token after login
TOKEN="YOUR_TOKEN_HERE"

# Test 1: Add high priority task
echo "1. Adding high priority task..."
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Add a high priority task: Complete report by Friday"}'

echo -e "\n\n2. List all tasks..."
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me all high priority tasks"}'

echo -e "\n\n3. Create tag..."
curl -X POST http://localhost:8000/api/chat \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message": "Create a tag called work with color #FF5733"}'

echo -e "\n\nDone!"
