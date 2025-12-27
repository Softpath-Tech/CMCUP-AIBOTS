#!/bin/bash

# Navigate to the app directory
echo "🚀 Starting CMCUP-AIBOTS Chatbot..."
cd "rag app" || { echo "❌ Could not find 'rag app' directory"; exit 1; }

# Run the Uvicorn server
uvicorn main:app --reload
