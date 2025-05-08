# app.py
import streamlit as st
import requests
import time
from datetime import datetime
import json
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

# Custom CSS for better UI
st.markdown("""
<style>
    /* Chat container styling */
    .chat-container {
        border-radius: 10px;
        margin-bottom: 10px;
        padding: 10px 15px;
        position: relative;
        max-width: 80%;
    }
    
    /* User message styling */
    .user-message {
        background-color: #e6f7ff;
        border-radius: 18px 18px 0 18px;
        float: right;
        clear: both;
        margin-left: 20%;
        color: black;
    }
    
    /* Bot message styling */
    .bot-message {
        background-color: #f0f2f6;
        border-radius: 18px 18px 18px 0;
        float: left;
        clear: both;
        margin-right: 20%;
        color: black;
    }
    
    /* Message metadata styling */
    .message-time {
        color: #888;
        font-size: 0.8em;
        margin-top: 5px;
        text-align: right;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stApp header {visibility: hidden;}
    
    /* Input box styling */
    .stTextInput div[data-baseweb="input"] {
        border-radius: 20px;
    }
    
    /* Message separator */
    .message-sep {
        height: 20px;
        clear: both;
    }
    
    /* Avatar styling */
    .avatar {
        border-radius: 50%;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-weight: bold;
        float: left;
        margin-right: 10px;
    }
    
    .user-avatar {
        background-color: #1f77b4;
    }
    
    .bot-avatar {
        background-color: #2ca02c;
    }
    
    /* Typing indicator */
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'is_typing' not in st.session_state:
    st.session_state.is_typing = False

# Function to send query to the API
def query_agent(query):
    try:
        response = requests.post(
            API_URL,
            json={"query": query},
            timeout=60
        )
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with the API: {str(e)}")
        return f"Sorry, I encountered an error: {str(e)}"

# Function to add a message to chat history
def add_message(role, content):
    timestamp = datetime.now().strftime("%H:%M")
    st.session_state.chat_history.append({
        "role": role,
        "content": content,
        "timestamp": timestamp
    })

# Function to display chat messages
def display_chat():
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        timestamp = message["timestamp"]
        
        if role == "user":
            # User message
            st.markdown(f"""
            <div class="chat-container user-message">
                <div style="display:flex; justify-content:space-between;">
                    <div class="avatar user-avatar">U</div>
                    <div style="flex-grow:1;">{content}</div>
                </div>
                <div class="message-time">{timestamp}</div>
            </div>
            <div class="message-sep"></div>
            """, unsafe_allow_html=True)
        else:
            # Bot message
            st.markdown(f"""
            <div class="chat-container bot-message">
                <div style="display:flex; justify-content:space-between;">
                    <div class="avatar bot-avatar">🔍</div>
                    <div style="flex-grow:1;">{content}</div>
                </div>
                <div class="message-time">{timestamp}</div>
            </div>
            <div class="message-sep"></div>
            """, unsafe_allow_html=True)
    
    # Display typing indicator if bot is typing
    if st.session_state.is_typing:
        st.markdown("""
        <div class="chat-container bot-message" style="max-width:150px;">
            <div style="display:flex; justify-content:space-between;">
                <div class="avatar bot-avatar">🔍</div>
                <div class="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
        <div class="message-sep"></div>
        """, unsafe_allow_html=True)

# Main app layout
st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown("Ask questions about your research documents and get intelligent answers.")

# Chat display area with fixed height
chat_container = st.container()
with chat_container:
    # Welcome message at the start
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="chat-container bot-message" style="max-width:90%;">
            <div style="display:flex; justify-content:space-between;">
                <div class="avatar bot-avatar">🔍</div>
                <div style="flex-grow:1;">
                    <b>Welcome to the Pinecone Research Assistant!</b><br>
                    I can help answer questions based on your research documents stored in the Pinecone vector database.
                    Ask me anything about your documents and I'll search for the most relevant information.
                </div>
            </div>
            <div class="message-time">{}</div>
        </div>
        <div class="message-sep"></div>
        """.format(datetime.now().strftime("%H:%M")), unsafe_allow_html=True)
    
    # Display chat history
    display_chat()

# Input area
with st.container():
    col1, col2 = st.columns([6, 1])
    # Create a callback for when the form is submitted
if "user_input" not in st.session_state:
    st.session_state.user_input = ""

def submit_message():
    if st.session_state.user_input:
        user_message = st.session_state.user_input
        # Add user message to chat
        add_message("user", user_message)
        # Clear input by setting an empty string (this happens before the widget is rendered again)
        st.session_state.user_input = ""
        # Set typing indicator
        st.session_state.is_typing = True
        st.rerun()

with col1:
    user_input = st.text_input("Ask a question:", key="user_input", 
                              on_change=submit_message, 
                              label_visibility="collapsed")
with col2:
    send_button = st.button("Send", on_click=submit_message, use_container_width=True)

# If typing, get response from API
if st.session_state.is_typing:
    user_query = st.session_state.chat_history[-1]["content"]
    
    # Get response from API
    bot_response = query_agent(user_query)
    
    # Add bot response to chat
    add_message("assistant", bot_response)
    
    # Turn off typing indicator
    st.session_state.is_typing = False
    st.rerun()

# Add a small footer
st.markdown("""
<div style="position:fixed; bottom:0; width:100%; text-align:center; padding:10px; font-size:0.8em; color:#888;">
    Powered by LangChain, OpenAI, and Pinecone
</div>
""", unsafe_allow_html=True)