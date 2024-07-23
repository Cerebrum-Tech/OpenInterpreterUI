import streamlit as st
import uuid
import json
from interpreter import interpreter
import os
from src.utils.prompts import PROMPTS

MODEL_PATH = os.path.join(os.getcwd(),'models.json')
def load_messages_from_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Assuming the JSON file is named 'system_messages.json' and is in the same directory
file_path = 'system_messages.json'
system_messages = load_messages_from_json(file_path)

# convert the JSON to text
messageString= json.dumps(system_messages)

system_message = (
        messageString
    )

def init_session_states():
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(f"No such file: '{MODEL_PATH}'")

    if 'models' not in st.session_state:
        with open(MODEL_PATH) as file:
            st.session_state['models'] = json.load(file)
    if 'api_choice' not in st.session_state:
        st.session_state['api_choice'] = None
    if 'chat_ready' not in st.session_state:
        st.session_state['chat_ready'] = False
    if 'system_message' not in st.session_state:
        st.session_state['system_message'] = system_message
    if 'user_id' not in st.session_state:
        st.session_state['user_id'] = str(uuid.uuid4())
    if 'interpreter' not in st.session_state:
        st.session_state['interpreter'] = interpreter