import streamlit as st
import json
from st_components.st_conversations import init_conversations
from st_components.st_messages import chat_with_interpreter
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from st_settings import settings_page  

# Database
from src.data.database import get_chats_by_conversation_id, save_conversation
from src.data.models import Conversation
import uuid



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
        load_settings()
        create_or_get_current_conversation()
        render_messages()
        chat_with_interpreter()
    else:
        create_or_get_current_conversation()
        render_messages()
        chat_with_interpreter()


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
        st.session_state.messages = get_chats_by_conversation_id(
            st.session_state['current_conversation']["id"]
        )


def render_messages():
    """
    Render Messages:
    Render chat-message when generated.
    """
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.chat_message(msg["role"]).markdown(
                f'<p>{msg["content"]}</p>', True)
        elif msg["role"] == "assistant":
            st.chat_message(msg["role"]).markdown(msg["content"])


def introduction():
    """
    Introduction:
    Display introductory messages for the user.
    """
    st.info("👋 Hey, we're very happy to see you here. 🤗")
    st.info("👉 Select the model from the menu to start the chat 🚀")

def load_settings():
    # read settings.json
    with open('settings.json', 'r') as f:
        settings = json.load(f)
    openai_key = os.environ.get('OPENAI_API_KEY', "")
    model = settings['model']
    context_window = settings['context_window']
    temperature = settings['temperature']
    max_tokens = settings['max_tokens']
    num_pair_messages_recall = settings['num_pair_messages_recall']
    system_promps = settings['system_message']
    os.environ["OPENAI_API_KEY"] = openai_key
    st.session_state['api_choice'] = 'openai'
    st.session_state['openai_key'] = openai_key
    st.session_state['model'] = model
    st.session_state['temperature'] = temperature
    st.session_state['max_tokens'] = max_tokens
    st.session_state['context_window'] = context_window
    st.session_state['num_pair_messages_recall'] = num_pair_messages_recall
    st.session_state['chat_ready'] = True
    st.success("Settings saved successfully!")
    st.session_state['system_message'] = system_promps