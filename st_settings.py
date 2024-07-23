import streamlit as st
import os
import json

PROMPTS_FILE = "prompts.json"

def load_prompts():
    if os.path.exists(PROMPTS_FILE):
        with open(PROMPTS_FILE, "r") as file:
            return json.load(file)
    return []

def save_prompts(prompts):
    with open(PROMPTS_FILE, "w") as file:
        json.dump(prompts, file)

def initialize_session_state():
    if 'openai_key' not in st.session_state:
        st.session_state['openai_key'] = os.getenv('OPENAI_API_KEY', '')
    if 'model' not in st.session_state:
        st.session_state['model'] = 'default_model'
    if 'temperature' not in st.session_state:
        st.session_state['temperature'] = 0.1
    if 'max_tokens' not in st.session_state:
        st.session_state['max_tokens'] = 600
    if 'context_window' not in st.session_state:
        st.session_state['context_window'] = 2048
    if 'num_pair_messages_recall' not in st.session_state:
        st.session_state['num_pair_messages_recall'] = 7
    if 'chat_ready' not in st.session_state:
        st.session_state['chat_ready'] = False

def settings_page():
    st.title("Settings")
    
    initialize_session_state()

    # Setup OpenAI Section
    st.subheader("OpenAI API Settings")
    
    model = st.selectbox(
        label='🔌 Models',
        options=list(st.session_state.get('models', {}).get('openai', {}).keys()),
        index=0,
    )
    context_window = st.session_state['models']['openai'][model]['context_window']
    temperature = st.slider('🌡 Temperature', min_value=0.01, max_value=1.0,
                            value=st.session_state.get('temperature', 0.1), step=0.01)
    max_tokens = st.slider('📝 Max tokens', min_value=1, max_value=2000,
                           value=st.session_state.get('max_tokens', 600), step=1)
    
    num_pair_messages_recall = st.slider(
        '*Memory Size*: User-assistant message pairs', min_value=1, max_value=10, value=7)

    if st.button("Save Settings 🚀"):
        st.session_state['api_choice'] = 'openai'
        st.session_state['model'] = model
        st.session_state['temperature'] = temperature
        st.session_state['max_tokens'] = max_tokens
        st.session_state['context_window'] = context_window
        st.session_state['num_pair_messages_recall'] = num_pair_messages_recall
        st.session_state['chat_ready'] = True
        st.success("Settings saved successfully!")

    # Prompts Section
    st.subheader("Prompts")

    prompts = load_prompts()

    
    with st.form(key='add_prompt_form'):
        new_prompt = st.text_area("New Prompt", value="", key='new_prompt_input')
        submit_button = st.form_submit_button("Add Prompt")

        if submit_button and new_prompt:
            prompts.append(new_prompt)
            save_prompts(prompts)
            st.success("Prompt added successfully!")
            st.experimental_rerun()  

  
    prompt_text = '\n'.join(prompts) if prompts else ""
    
   
    with st.container():
        st.text_area("Current Prompts", value=prompt_text, key='prompts_text_area_display', height=200)
        
        
        if st.button("Delete All Prompts"):
            if not prompts:
                st.warning("No prompts to delete.")
            else:
                save_prompts([])
                st.success("All prompts deleted!")
                st.experimental_rerun()  

if __name__ == "__main__":
    settings_page()
