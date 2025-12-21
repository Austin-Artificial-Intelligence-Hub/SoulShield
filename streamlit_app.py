#!/usr/bin/env python3
"""
SoulShield - Privacy-Focused AI Wellness Companion
A supportive conversational AI designed with mental wellness in mind
"""

import streamlit as st
import requests
import json
from datetime import datetime
import uuid

# Page config
st.set_page_config(
    page_title="SoulShield - AI Wellness Companion",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS inspired by The Good Mental Health Company
st.markdown("""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main theme colors inspired by mental health websites */
    :root {
        --primary-blue: #4A90E2;       /* Soft Blue */
        --secondary-blue: #7BB3F0;     /* Light Blue */
        --accent-blue: #B8D4F0;       /* Very Light Blue */
        --warm-orange: #FF8C42;        /* Warm Orange */
        --light-orange: #FFB380;       /* Light Orange */
        --background-main: #FEFEFE;    /* Almost White */
        --background-light: #F8FBFF;   /* Very Light Blue */
        --background-card: #FFFFFF;    /* Pure White */
        --text-primary: #2C3E50;       /* Dark Blue Gray */
        --text-secondary: #5A6C7D;     /* Medium Blue Gray */
        --success-color: #27AE60;      /* Green */
        --warning-color: #F39C12;      /* Orange */
        --error-color: #E74C3C;        /* Red */
    }
    
    /* Override Streamlit's default dark theme */
    .stApp {
        background: var(--background-main) !important;
        color: var(--text-primary) !important;
    }
    
    /* Global styling */
    .main {
        background: linear-gradient(135deg, var(--background-main) 0%, var(--background-light) 100%) !important;
        font-family: 'Inter', sans-serif !important;
        color: var(--text-primary) !important;
    }
    
    /* Force bright background */
    .stApp > div {
        background: var(--background-main) !important;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, var(--primary-blue), var(--warm-orange));
        padding: 2rem 0;
        border-radius: 0 0 20px 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 600;
        margin: 0;
        text-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
        opacity: 0.95;
    }
    
    /* Sidebar styling */
    .css-1d391kg, .css-1cypcdb {
        background: linear-gradient(180deg, var(--background-card) 0%, var(--background-light) 100%) !important;
        border-right: 3px solid var(--accent-blue) !important;
    }
    
    /* Sidebar text color */
    .css-1d391kg *, .css-1cypcdb * {
        color: var(--text-primary) !important;
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: var(--background-card) !important;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 15px rgba(74, 144, 226, 0.1);
        border-left: 4px solid var(--secondary-blue);
        color: var(--text-primary) !important;
    }
    
    /* User message styling */
    .stChatMessage[data-testid="user-message"] {
        background: linear-gradient(135deg, var(--primary-blue), var(--secondary-blue)) !important;
        color: white !important;
        border-left: 4px solid var(--warm-orange);
    }
    
    /* Assistant message styling */
    .stChatMessage[data-testid="assistant-message"] {
        background: var(--background-card) !important;
        border-left: 4px solid var(--warm-orange);
        color: var(--text-primary) !important;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-blue), var(--warm-orange)) !important;
        color: white !important;
        border: none !important;
        border-radius: 25px;
        padding: 0.5rem 1.5rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(74, 144, 226, 0.4);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        background: var(--background-card) !important;
        color: var(--text-primary) !important;
        border-radius: 15px;
        border: 2px solid var(--accent-blue) !important;
        padding: 0.75rem;
        font-family: 'Inter', sans-serif;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: var(--primary-blue) !important;
        box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.2) !important;
    }
    
    /* Card styling */
    .wellness-card {
        background: var(--background-card) !important;
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.1);
        border: 1px solid var(--accent-blue);
        color: var(--text-primary) !important;
    }
    
    /* Success/Info/Error styling */
    .stSuccess {
        background: linear-gradient(135deg, var(--success-color), #58D68D) !important;
        border-radius: 15px;
        border: none !important;
        color: white !important;
    }
    
    .stInfo {
        background: linear-gradient(135deg, var(--secondary-blue), var(--accent-blue)) !important;
        border-radius: 15px;
        border: none !important;
        color: var(--text-primary) !important;
    }
    
    .stError {
        background: linear-gradient(135deg, var(--error-color), #F1948A) !important;
        border-radius: 15px;
        border: none !important;
        color: white !important;
    }
    
    /* Expander styling */
    .streamlit-expanderHeader {
        background: var(--background-light) !important;
        border-radius: 10px;
        border: 1px solid var(--accent-blue) !important;
        color: var(--text-primary) !important;
    }
    
    /* Chat input styling */
    .stChatInputContainer {
        background: var(--background-card) !important;
        border-radius: 25px;
        border: 2px solid var(--accent-blue) !important;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.1);
    }
    
    /* Chat input text */
    .stChatInput input {
        background: var(--background-card) !important;
        color: var(--text-primary) !important;
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--accent-blue), transparent);
        margin: 2rem 0;
    }
    
    /* Caption styling */
    .caption {
        color: var(--text-secondary) !important;
        font-size: 0.9rem;
        font-style: italic;
    }
    
    /* Sidebar section headers */
    .sidebar-header {
        color: var(--primary-blue) !important;
        font-weight: 600;
        font-size: 1.1rem;
        margin: 1rem 0 0.5rem 0;
    }
    
    /* Privacy badge */
    .privacy-badge {
        background: linear-gradient(135deg, var(--primary-blue), var(--warm-orange));
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 2px 10px rgba(74, 144, 226, 0.3);
    }
    
    /* Welcome message */
    .welcome-message {
        background: linear-gradient(135deg, var(--warm-orange), var(--light-orange));
        color: white;
        padding: 1rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(255, 140, 66, 0.3);
    }
    
    /* Radio button styling */
    .stRadio > div {
        background: var(--background-card) !important;
        border-radius: 10px;
        padding: 0.5rem;
    }
    
    /* Select box styling */
    .stSelectbox > div > div {
        background: var(--background-card) !important;
        color: var(--text-primary) !important;
    }
    
    /* Metric styling */
    .metric-container {
        background: var(--background-card) !important;
        color: var(--text-primary) !important;
    }
    
    /* Override any remaining dark elements */
    div[data-testid="stSidebar"] {
        background: var(--background-light) !important;
    }
    
    /* Text elements */
    p, span, div {
        color: var(--text-primary) !important;
    }
    
    /* Headers */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text-primary) !important;
    }
</style>
""", unsafe_allow_html=True)

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
    """Show user's chat summaries with improved styling"""
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
                st.markdown('<div class="sidebar-header">📊 Your Conversation Summaries</div>', unsafe_allow_html=True)
                for summary in summaries:
                    session_date = datetime.fromtimestamp(summary['created_at']).strftime('%B %d, %Y at %H:%M')
                    with st.expander(f"💭 Session from {session_date}"):
                        st.markdown(f"""
                        <div class="wellness-card">
                            <p style="color: var(--text-primary); line-height: 1.6;">
                                {summary['summary']}
                            </p>
                            <small style="color: var(--text-secondary);">
                                Session ID: {summary['sessionId'][:12]}...
                            </small>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="wellness-card" style="text-align: center;">
                    <h4 style="color: var(--primary-color);">🌱 No Summaries Yet</h4>
                    <p style="color: var(--text-secondary);">
                        Start a longer conversation to generate your first summary! 
                        Summaries help me remember our previous discussions.
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("Unable to load your summaries right now. Please try again later.")
            
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

# Custom header with navigation
st.markdown("""
<div class="main-header">
    <div style="display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 2rem;">
        <div>
            <h1>🛡️ SoulShield</h1>
            <p>Your Privacy-First AI Wellness Companion</p>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Navigation menu in the main area (since Streamlit tabs can't be moved to header)
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'Home'

# Create navigation buttons in the top right area
col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])

with col2:
    if st.button("🏠 Home", use_container_width=True):
        st.session_state.current_page = 'Home'

with col3:
    if st.button("ℹ️ About", use_container_width=True):
        st.session_state.current_page = 'About'

with col4:
    if st.button("✨ Features", use_container_width=True):
        st.session_state.current_page = 'Features'

with col5:
    if st.button("📞 Contact", use_container_width=True):
        st.session_state.current_page = 'Contact'

# Sidebar for configuration and authentication
with st.sidebar:
    st.markdown('<div class="sidebar-header">⚙️ Configuration</div>', unsafe_allow_html=True)
    
    api_url = st.text_input(
        "API URL",
        value=st.session_state.get('api_url', 'https://ddnokfk0l0.execute-api.us-east-1.amazonaws.com/prod/'),
        placeholder="https://your-api.execute-api.region.amazonaws.com/prod/",
        help="Your AWS API Gateway URL"
    )
    
    api_key = st.text_input(
        "API Key",
        value=st.session_state.get('api_key', 'XAdPWDF2S070NeGzSGGRL26zYX8x2Apm9enCyL2F'),
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
        st.markdown('<div class="sidebar-header">🔐 Account Access</div>', unsafe_allow_html=True)
        
        auth_tab = st.radio("Choose action:", ["Login", "Register"], horizontal=True)
        
        username = st.text_input("Username", key="auth_username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", key="auth_password", placeholder="Enter your password")
        
        if auth_tab == "Register":
            if st.button("🌟 Create Account", use_container_width=True):
                if username and password:
                    success = register_user(api_url, api_key, username, password)
                    if success:
                        st.success("🎉 Account created successfully! Please login.")
                        st.rerun()
                else:
                    st.error("Please enter both username and password")
        else:
            if st.button("🚀 Login", use_container_width=True):
                if username and password:
                    token = login_user(api_url, api_key, username, password)
                    if token:
                        st.session_state.user_token = token
                        st.session_state.username = username
                        st.success(f"Welcome back, {username}! 🌈")
                        st.rerun()
                else:
                    st.error("Please enter both username and password")
    else:
        st.markdown(f'<div class="welcome-message">👋 Welcome back, <strong>{st.session_state.username}</strong>!</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 View Summaries", use_container_width=True):
                show_summaries(api_url, api_key, st.session_state.user_token)
        with col2:
            if st.button("🚪 Logout", use_container_width=True):
                st.session_state.user_token = None
                st.session_state.username = None
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                st.rerun()
    
    st.divider()
    
    # Session info
    st.markdown('<div class="sidebar-header">📱 Session Info</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="wellness-card"><strong>Session:</strong> {st.session_state.session_id[:8]}...<br><strong>Messages:</strong> {len(st.session_state.messages)}</div>', unsafe_allow_html=True)
    
    if st.button("🔄 New Conversation", use_container_width=True):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()
    
    st.divider()
    
    # Privacy notice
    st.markdown('<div class="sidebar-header">🔒 Privacy Promise</div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="privacy-badge">
        <strong>Your Privacy Matters</strong><br>
        🔐 End-to-end encryption<br>
        🗑️ Auto-deletion after 30 days<br>
        💾 Secure chat summaries<br>
        🛡️ No data sharing
    </div>
    """, unsafe_allow_html=True)

# Main interface based on current page
if not st.session_state.user_token:
    # Show welcome page with navigation for non-authenticated users
    
    if st.session_state.current_page == 'Home':
        # Home page with image and content side by side
        col1, col2 = st.columns([1, 1])
        
        with col1:
            # Add a wellness-themed image placeholder
            st.markdown("""
            <div style="background: linear-gradient(135deg, #FFB380, #FF8C42); 
                        border-radius: 50%; width: 300px; height: 300px; margin: 2rem auto;
                        display: flex; align-items: center; justify-content: center; color: white;
                        box-shadow: 0 10px 30px rgba(255, 140, 66, 0.3);">
                <div style="text-align: center; font-size: 4rem;">
                    🧠<br>
                    <div style="font-size: 1rem; margin-top: 1rem;">Mental Wellness<br>& Privacy</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("## Affordable, high-quality AI therapy delivered with heart & soul")
            st.write("""
            **SoulShield** provides privacy-focused conversational AI sessions available online 
            with complete data protection and intelligent memory for continuity across sessions.
            """)
            
            st.success("**✨ What makes SoulShield special?**\n\n🛡️ Complete privacy protection\n\n🧠 Remembers your conversations\n\n💚 Designed with wellness in mind\n\n🔒 Your data never leaves your control")
            
            if st.button("🚀 Start Your Journey", use_container_width=True, type="primary"):
                st.info("👈 Create an account in the sidebar to get started!")
    
    elif st.session_state.current_page == 'About':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### About SoulShield")
            
            st.markdown("#### 🎯 Our Mission")
            st.write("""
            SoulShield is designed to provide a safe, private space for meaningful conversations with AI. 
            We believe that everyone deserves access to supportive dialogue while maintaining complete 
            control over their personal information.
            """)
            
            st.markdown("#### 🔒 Privacy First")
            st.write("""
            Unlike other AI platforms, SoulShield is built with privacy as the foundation. Your conversations 
            are encrypted, automatically deleted after 30 days, and never used to train other models. 
            Your data stays yours.
            """)
            
            st.markdown("#### 🧠 Intelligent Memory")
            st.write("""
            SoulShield creates thoughtful summaries of your conversations, allowing for continuity across 
            sessions while respecting your privacy. This means more meaningful, contextual interactions 
            over time.
            """)
            
            st.info("🌟 **Built by Austin AI Hub** - Developed with care by the Austin Artificial Intelligence Hub, committed to ethical AI and user empowerment.")
    
    elif st.session_state.current_page == 'Features':
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🛡️ Privacy Features")
            st.write("- **End-to-end encryption** - All messages secured in transit")
            st.write("- **Auto-deletion** - Data removed after 30 days")
            st.write("- **No tracking** - We don't monitor or analyze your behavior")
            st.write("- **Local control** - Your data stays in your AWS account")
            st.write("- **Secure authentication** - PBKDF2 password hashing")
        
        with col2:
            st.markdown("#### ✨ Smart Features")
            st.write("- **Conversation memory** - Remembers context across sessions")
            st.write("- **Smart summaries** - AI-generated conversation insights")
            st.write("- **Multiple sessions** - Organize different conversation topics")
            st.write("- **AWS Bedrock** - Powered by Claude for thoughtful responses")
            st.write("- **Responsive design** - Works on all devices")
        
        st.markdown("#### 🚀 Getting Started")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            st.info("**1. Create Account**\n\nSign up in the sidebar")
        with col_b:
            st.info("**2. Start Chatting**\n\nBegin your conversation")
        with col_c:
            st.info("**3. View Summaries**\n\nTrack your progress")
    
    elif st.session_state.current_page == 'Contact':
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### 📞 Get in Touch")
            
            st.success("🏢 **Austin Artificial Intelligence Hub** - We're a community-driven organization focused on ethical AI development and empowering users with privacy-first solutions.")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                st.markdown("#### 🌐 GitHub")
                st.write("Find our open-source code and contribute to the project")
                st.markdown("[View Repository →](https://github.com/Austin-Artificial-Intelligence-Hub/SoulShield)")
            
            with col_b:
                st.markdown("#### 💬 Support")
                st.write("Need help or have questions about SoulShield?")
                st.markdown("[Create Issue →](https://github.com/Austin-Artificial-Intelligence-Hub/SoulShield/issues)")
            
            st.info("🤝 **Join Our Community** - Interested in ethical AI development? We welcome contributors, researchers, and anyone passionate about privacy-first technology.")

else:
    # Authenticated user interface with chat tabs
    tab1, tab2, tab3 = st.tabs(["💬 Chat", "📊 My Summaries", "⚙️ Settings"])
    
    with tab1:
        # Chat messages container
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown('<div class="wellness-card">', unsafe_allow_html=True)
            
            # Display chat messages
            if not st.session_state.messages:
                st.info("🌱 **Start Your Conversation** - I'm here to listen and support you. Feel free to share what's on your mind, ask questions, or just have a friendly chat. Your privacy and wellbeing are my top priorities.")
            
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
                    if "timestamp" in message:
                        st.markdown(f'<div class="caption">💬 {message["timestamp"]}</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    with tab2:
        st.markdown("### 📊 Your Conversation Summaries")
        st.write("Track your conversations and see how your discussions have evolved over time.")
        
        # Show summaries
        show_summaries(api_url, api_key, st.session_state.user_token)
    
    with tab3:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("### ⚙️ Account Settings")
            
            st.info(f"**👤 Account Information**\n\n**Username:** {st.session_state.username}\n\n**Session ID:** {st.session_state.session_id[:12]}...\n\n**Messages in current session:** {len(st.session_state.messages)}")
            
            st.success("**🔒 Privacy Settings**\n\n✅ End-to-end encryption enabled\n\n✅ Auto-deletion after 30 days\n\n✅ Secure password hashing\n\n✅ No data sharing with third parties")
            
            st.write("Need to start fresh or switch accounts? Use the logout button in the sidebar.")

# Chat input (only show when logged in and on chat tab)
if st.session_state.user_token:
    if prompt := st.chat_input("Share what's on your mind... 💭", key="chat_input"):
        # Check if API is configured and user is logged in
        if not api_url or not api_key:
            st.error("⚠️ Please configure your API settings in the sidebar")
            st.stop()
        
        if not st.session_state.user_token:
            st.error("⚠️ Please login to start your wellness journey")
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
            st.markdown(f'<div class="caption">💬 {timestamp}</div>', unsafe_allow_html=True)
        
        # Call API
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 Thinking thoughtfully...")
            
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
                    assistant_message = data.get('response', 'I apologize, but I didn\'t receive a proper response. Please try again.')
                    
                    # Update placeholder with actual response
                    message_placeholder.markdown(assistant_message)
                    current_time = datetime.now().strftime("%H:%M:%S")
                    st.markdown(f'<div class="caption">🤖 {current_time}</div>', unsafe_allow_html=True)
                    
                    # Add to session state
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": assistant_message,
                        "timestamp": current_time
                    })
                    
                elif response.status_code == 401:
                    message_placeholder.error("🔐 Your session has expired. Please login again to continue.")
                    st.session_state.user_token = None
                    st.session_state.username = None
                else:
                    error_msg = f"I encountered an issue (Error {response.status_code}). Please try again in a moment."
                    message_placeholder.error(error_msg)
                    
            except requests.exceptions.Timeout:
                message_placeholder.error("⏱️ The request took too long. Please try again.")
            except requests.exceptions.ConnectionError:
                message_placeholder.error("🔌 Connection issue. Please check your internet connection.")
            except Exception as e:
                message_placeholder.error(f"❌ Something unexpected happened. Please try again.")

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; padding: 2rem; background: var(--background-light); border-radius: 15px; margin-top: 2rem;">
    <h4 style="color: var(--primary-color); margin-bottom: 1rem;">🛡️ SoulShield Promise</h4>
    <p style="color: var(--text-secondary); margin: 0;">
        Built with privacy, security, and your wellbeing at heart • 
        <strong>Your conversations are safe</strong> • 
        Data automatically deleted after 30 days • 
        <strong>You are in control</strong>
    </p>
</div>
""", unsafe_allow_html=True)