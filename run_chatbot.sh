#!/bin/bash

echo "🚀 Starting your AI Chatbot..."
echo ""
echo "Your credentials:"
echo "API URL: https://ddnokfk0l0.execute-api.us-east-1.amazonaws.com/prod/"
echo "API Key: XAdPWDF2S070NeGzSGGRL26zYX8x2Apm9enCyL2F"
echo ""
echo "The browser will open automatically at http://localhost:8501"
echo "Enter your credentials in the sidebar to start chatting!"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Activate virtual environment and run streamlit
source soul-env/bin/activate
streamlit run streamlit_app.py
