import json
import streamlit as st
from st_components.st_conversations import init_conversations
from st_components.st_messages import chat_with_interpreter
import sys
import os
import uuid

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from st_settings import settings_page  

# Database
from src.data.database import get_chats_by_conversation_id, save_conversation
from src.data.models import Conversation

CHATS_DIR = 'chats'

def st_main():
    st.markdown("""
    <style>
        .reportview-container {
            margin-top: -2em;
        }
        #MainMenu {visibility: hidden;}
        .stDeployButton {display:none;}
        footer {visibility: hidden;}
        #stDecoration {display:none;}
    </style>
    """, unsafe_allow_html=True)

    if not st.session_state.get('chat_ready', False):
        introduction()
    else:
        create_or_get_current_conversation()
        render_messages()
        chat_with_interpreter()

def get_user_id():
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = str(uuid.uuid4())
    return st.session_state['user_id']

def save_chat(chat):
    user_id = st.session_state['user_id']
    filename = os.path.join(CHATS_DIR, f'{user_id}_chats.json')
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            chats = json.load(f)
    else:
        chats = []
    chats.append(chat)
    with open(filename, 'w') as f:
        json.dump(chats, f)

def load_chats():
    user_id = st.session_state['user_id']
    filename = os.path.join(CHATS_DIR, f'{user_id}_chats.json')
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def create_or_get_current_conversation():
    if 'current_conversation' not in st.session_state:
        conversations, conversation_options = init_conversations()
        if conversations:
            st.session_state['current_conversation'] = conversations[0]
        else:
            conversation_id = str(uuid.uuid4())
            new_conversation = Conversation(
                conversation_id, st.session_state.user_id, f"Conversation {len(conversations)}")
            save_conversation(new_conversation)
            st.session_state['current_conversation'] = {
                "id": new_conversation.id,
                "user_id": new_conversation.user_id,
                "name": new_conversation.name
            }
            st.session_state["messages"] = []
            st.rerun()
    else:
        st.session_state.messages = load_chats()

def render_messages():
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message(msg["role"]).markdown(f'<p>{msg["content"]}</p>', True)
        elif msg["role"] == "assistant":
            st.chat_message(msg["role"]).markdown(msg["content"])

def introduction():
    st.info("👋 Hey, we're very happy to see you here. 🤗")
    st.info("👉 Select the model from the menu to start the chat 🚀")