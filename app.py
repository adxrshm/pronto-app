import streamlit as st
import requests
import time
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/query")
APP_TITLE = "Research Assistant"
APP_ICON = "🔍"

# Page configuration
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    /* Existing styles */
    .chat-container {
        border-radius: 10px;
        margin-bottom: 10px;
        padding: 10px 14px;
        position: relative;
        width: fit-content;
        max-width: 70%;
        display: inline-block;
        align-items: flex-start;
    }

    .user-message {
        background-color: #e6f7ff;
        border-radius: 18px 18px 0 18px;
        margin-left: 20px;
        margin-right: 20px;
        color: black;
    }

    .bot-message {
        background-color: #f0f2f6;
        border-radius: 18px 18px 18px 0;
        margin-left: 20px;
        margin-right: 20px;
        color: black;
    }

    .message-time {
        color: #888;
        font-size: 0.75em;
        margin-top: 4px;
        margin-left: 20px;
        margin-right: 20px;
        text-align: right;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp header {visibility: hidden;}

    .stTextInput div[data-baseweb="input"] {
        border-radius: 20px;
    }

    .message-sep {
        height: 15px;
        clear: both;
    }

    .avatar {
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        flex-shrink: 0;
        margin-right: 10px;
        margin-top: 4px;
    }

    .user-avatar {
        background-color: #1f77b4;
        order: 2;
        margin-left: 10px;
        margin-right: 20px;
    }

    .bot-avatar {
        background-color: #2ca02c;
        order: 0;
        margin-left: 20px;
    }

    .typing-indicator {
        display: inline-block;
        position: relative;
        padding: 10px 15px;
        background-color: #f0f2f6;
        border-radius: 18px;
    }

    .typing-indicator span {
        height: 8px;
        width: 8px;
        background-color: #888;
        border-radius: 50%;
        display: inline-block;
        margin-right: 3px;
        animation: typing 1s infinite;
    }

    .typing-indicator span:nth-child(1) {
        animation-delay: 0s;
    }

    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }

    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
        margin-right: 0;
    }

    @keyframes typing {
        0% { transform: translateY(0px); }
        50% { transform: translateY(-5px); }
        100% { transform: translateY(0px); }
    }

    /* New rule to hide the yellow warning message */
    div.stAlert[data-testid="stAlert"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'is_typing' not in st.session_state:
    st.session_state.is_typing = False

# API query
def query_agent(query):
    try:
        response = requests.post(API_URL, json={"query": query}, timeout=60)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"

# Add message
def add_message(role, content):
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

# Display chat
def display_chat():
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        timestamp = message["timestamp"]

        if role == "user":
            st.write(f"""
            <div style="display:flex; justify-content:flex-end;">
                <div class="chat-container user-message">{content}</div>
                <div class="avatar user-avatar">U</div>
            </div>
            <div class="message-time" style="text-align:right; margin-right:50px;">{timestamp}</div>
            <div class="message-sep"></div>
            """, unsafe_allow_html=True)
        else:
            st.write(f"""
            <div style="display:flex; justify-content:flex-start;">
                <div class="avatar bot-avatar">🔍</div>
                <div class="chat-container bot-message">{content}</div>
            </div>
            <div class="message-time" style="text-align:left; margin-left:50px;">{timestamp}</div>
            <div class="message-sep"></div>
            """, unsafe_allow_html=True)

    # Typing indicator
    if st.session_state.is_typing:
        st.markdown("""
        <div style="display:flex; justify-content:flex-start;">
            <div class="avatar bot-avatar">🔍</div>
            <div class="chat-container bot-message" style="max-width:150px;">
                <div class="typing-indicator">
                    <span></span><span></span><span></span>
                </div>
            </div>
        </div>
        <div class="message-sep"></div>
        """, unsafe_allow_html=True)

# Title and instructions
st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown("Ask questions about your research documents and get intelligent answers.")

# Chat display area
chat_container = st.container()
with chat_container:
    if not st.session_state.chat_history:
        pass

    display_chat()

# Input
with st.container():
    col1, col2 = st.columns([6, 1])

if "user_input" not in st.session_state:
    st.session_state.user_input = ""

def submit_message():
    if st.session_state.user_input:
        user_message = st.session_state.user_input
        add_message("user", user_message)
        st.session_state.user_input = ""
        st.session_state.is_typing = True
        st.rerun()

with col1:
    st.text_input("Ask a question:", key="user_input", 
                  on_change=submit_message, label_visibility="collapsed")

with col2:
    st.button("Send", on_click=submit_message, use_container_width=True)

# Bot response
if st.session_state.is_typing:
    user_query = st.session_state.chat_history[-1]["content"]
    bot_response = query_agent(user_query)
    add_message("assistant", bot_response)
    st.session_state.is_typing = False
    st.rerun()


