import streamlit as st
import json
import os
from src.utils.prompts import PROMPTS

def settings_page():
    st.title("Settings")

    # Setup OpenAI Section
    st.subheader("OpenAI API Settings")
    openai_key = os.environ.get('OPENAI_API_KEY', "")
    model = st.selectbox(
        label='🔌 Models',
        options=list(st.session_state.get('models', {}).get('openai', {}).keys()),
        index= 0 if st.session_state.get('model') is None else list(st.session_state.get('models', {}).get('openai', {}).keys()).index(st.session_state.get('model'))
    )
    context_window = st.session_state['models']['openai'][model]['context_window']
    temperature = st.slider('🌡 Temperature', min_value=0.01, max_value=1.0,
                            value=st.session_state.get('temperature', 0.1), step=0.01)
    max_tokens = st.slider('📝 Max tokens', min_value=1, max_value=2000,
                           value=st.session_state.get('max_tokens', 600), step=1)

    num_pair_messages_recall = st.slider(
        'Memory Size: User-assistant message pairs', min_value=1, max_value=10, value=7)

    button_container = st.empty()
    save_button = button_container.button("Save Settings 🚀", key='save_model_configs')

    system_promps = st.text_area("System Message", value=st.session_state.get('system_message'))

    if save_button:
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
        # Save the settings to a file
        with open('settings.json', 'w') as f:
            json.dump({
                "model": model,
                "temperature": temperature,
                "max_tokens": max_tokens,
                "context_window": context_window,
                "num_pair_messages_recall": num_pair_messages_recall,
                "system_message": system_promps
            }, f)
        # restart the app
    # Prompts Section