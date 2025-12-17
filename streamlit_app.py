#!/usr/bin/env python3
"""
Streamlit Chat Interface for Privacy-Focused Chatbot
A general-purpose conversational AI for customer service, education, etc.
"""

import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Page config
st.set_page_config(
    page_title="AI Assistant",
    page_icon="💬",
    layout="centered"
)

# Helper functions
def register_user(api_url: str, api_key: str, username: str, password: str) -> bool:
    """Register a new user"""
    try:
        endpoint = api_url.rstrip('/') + '/auth/register'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }
        payload = {
            'username': username,
            'password': password
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            return True
        else:
            data = response.json()
            st.error(f"Registration failed: {data.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        st.error(f"Registration error: {str(e)}")
        return False


def login_user(api_url: str, api_key: str, username: str, password: str) -> str:
    """Login user and return token"""
    try:
        endpoint = api_url.rstrip('/') + '/auth/login'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }
        payload = {
            'username': username,
            'password': password
        }
        
        response = requests.post(endpoint, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('token')
        else:
            data = response.json()
            st.error(f"Login failed: {data.get('error', 'Unknown error')}")
            return None
            
    except Exception as e:
        st.error(f"Login error: {str(e)}")
        return None


def show_summaries(api_url: str, api_key: str, token: str):
    """Show user's chat summaries"""
    try:
        endpoint = api_url.rstrip('/') + '/summaries'
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': api_key
        }
        params = {'token': token}
        
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            summaries = data.get('summaries', [])
            
            if summaries:
                st.subheader("📊 Your Chat Summaries")
                for summary in summaries:
                    with st.expander(f"Session {summary['sessionId'][:8]}... - {datetime.fromtimestamp(summary['created_at']).strftime('%Y-%m-%d %H:%M')}"):
                        st.write(summary['summary'])
            else:
                st.info("No chat summaries yet. Start a longer conversation to generate summaries!")
        else:
            st.error("Failed to load summaries")
            
    except Exception as e:
        st.error(f"Error loading summaries: {str(e)}")

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'user_token' not in st.session_state:
    st.session_state.user_token = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'show_login' not in st.session_state:
    st.session_state.show_login = True

# Sidebar for configuration and authentication
with st.sidebar:
    st.title("⚙️ Configuration")
    
    api_url = st.text_input(
        "API URL",
        value=st.session_state.get('api_url', ''),
        placeholder="https://your-api.execute-api.region.amazonaws.com/prod/",
        help="Your AWS API Gateway URL"
    )
    
    api_key = st.text_input(
        "API Key",
        value=st.session_state.get('api_key', ''),
        type="password",
        placeholder="Enter your API key",
        help="Your API Gateway API key"
    )
    
    # Save to session state
    st.session_state.api_url = api_url
    st.session_state.api_key = api_key
    
    st.divider()
    
    # Authentication section
    if not st.session_state.user_token:
        st.subheader("🔐 Login / Register")
        
        auth_tab = st.radio("Choose action:", ["Login", "Register"], horizontal=True)
        
        username = st.text_input("Username", key="auth_username")
        password = st.text_input("Password", type="password", key="auth_password")
        
        if auth_tab == "Register":
            if st.button("Create Account", use_container_width=True):
                if username and password:
                    success = register_user(api_url, api_key, username, password)
                    if success:
                        st.success("Account created! Please login.")
                        st.rerun()
                else:
                    st.error("Please enter username and password")
        else:
            if st.button("Login", use_container_width=True):
                if username and password:
                    token = login_user(api_url, api_key, username, password)
                    if token:
                        st.session_state.user_token = token
                        st.session_state.username = username
                        st.success(f"Welcome back, {username}!")
                        st.rerun()
                else:
                    st.error("Please enter username and password")
    else:
        st.subheader(f"👋 Welcome, {st.session_state.username}!")
        
        if st.button("📊 View Chat Summaries", use_container_width=True):
            show_summaries(api_url, api_key, st.session_state.user_token)
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user_token = None
            st.session_state.username = None
            st.session_state.messages = []
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    
    st.divider()
    
    # Session info
    st.subheader("Session Info")
    st.caption(f"Session ID: {st.session_state.session_id[:8]}...")
    st.caption(f"Messages: {len(st.session_state.messages)}")
    
    if st.button("🔄 New Session", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Privacy notice
    st.subheader("🔒 Privacy")
    st.caption("• Messages encrypted in transit")
    st.caption("• Auto-deleted after 30 days")
    st.caption("• Chat summaries stored per user")
    st.caption("• Secure password hashing")

# Main chat interface
st.title("💬 AI Assistant with Memory")
st.caption("A privacy-focused conversational AI with user accounts and chat summaries")

# Show login prompt if not authenticated
if not st.session_state.user_token:
    st.info("👈 Please login or register in the sidebar to start chatting")
    st.stop()

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "timestamp" in message:
            st.caption(message["timestamp"])

# Chat input
if prompt := st.chat_input("Type your message here..."):
    # Check if API is configured and user is logged in
    if not api_url or not api_key:
        st.error("⚠️ Please configure API URL and API Key in the sidebar")
        st.stop()
    
    if not st.session_state.user_token:
        st.error("⚠️ Please login to start chatting")
        st.stop()
    
    # Add user message to chat
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "timestamp": timestamp
    })
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)
        st.caption(timestamp)
    
    # Call API
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")
        
        try:
            # Ensure URL ends with /
            endpoint = api_url.rstrip('/') + '/chat'
            
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': api_key
            }
            
            payload = {
                'message': prompt,
                'sessionId': st.session_state.session_id,
                'token': st.session_state.user_token
            }
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                assistant_message = data.get('response', 'No response received')
                
                # Update placeholder with actual response
                message_placeholder.markdown(assistant_message)
                st.caption(datetime.now().strftime("%H:%M:%S"))
                
                # Add to session state
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_message,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                
            elif response.status_code == 401:
                message_placeholder.error("🔐 Session expired. Please login again.")
                st.session_state.user_token = None
                st.session_state.username = None
            else:
                error_msg = f"Error: {response.status_code} - {response.text}"
                message_placeholder.error(error_msg)
                
        except requests.exceptions.Timeout:
            message_placeholder.error("⏱️ Request timed out. Please try again.")
        except requests.exceptions.ConnectionError:
            message_placeholder.error("🔌 Connection error. Check your API URL.")
        except Exception as e:
            message_placeholder.error(f"❌ Error: {str(e)}")

# Footer
st.divider()
st.caption("Built with privacy in mind • User accounts • Chat summaries • Auto-deleted after 30 days")