import streamlit as st
import os
from langdetect import detect

INTERPRETER_DIR = os.path.join(os.getcwd(), 'interpreter')


def setup_interpreter():
    try:
        st.session_state['interpreter'].reset()
    except:
        pass
    os.chdir(INTERPRETER_DIR)
    st.session_state['interpreter'].conversation_filename = st.session_state['current_conversation']["id"]
    st.session_state['interpreter'].conversation_history = True
    st.session_state['interpreter'].messages = st.session_state.get(
        'messages',
        st.session_state.get('mensajes', [])
    )
    
    
    st.session_state['interpreter'].llm.model = st.session_state['model']
    st.session_state['interpreter'].llm.temperature = st.session_state['temperature']
    st.session_state['interpreter'].llm.max_tokens = st.session_state['max_tokens']
    st.session_state['interpreter'].llm.custom_instructions = """
    Provide detailed analytical insights when responding to queries.
    Prioritize accuracy and clarity in your explanations.
    Use visual aids like charts and graphs when possible.
    When asked for data analysis, provide detailed insights including statistical summaries and visualizations.
    Use libraries like pandas for data manipulation and matplotlib or seaborn for visualizations.
    Ensure visualizations are clear and well-labeled.
    Always provide accurate and detailed explanations in your responses.
    If a query involves complex data, break down the explanation into simpler parts.
    Use examples and visual aids where appropriate to enhance understanding.
    When generating reports, include key metrics and trends.
    Provide actionable insights and recommendations based on the data analysis.
    Highlight any anomalies or significant patterns observed in the data.
    When asked to create a map, use the Folium library.
    Ensure the map includes relevant data points with proper markers and pop-ups.
    For example, to create a map with data points:
    1. Import the Folium library.
    2. Create a base map centered at a specific location.
    3. Add markers to the map for each data point.
    4. Save the map as an HTML file and provide a link to the user.
    Run shell commands with -y so the user doesn't have to confirm them.
    Detect the language of the user's query and respond in the same language.
    """
    
    st.session_state['interpreter'].auto_run = True

    st.session_state['interpreter'].computer.emit_images = True

    if st.session_state['api_choice'] == 'openrouter':
        st.session_state['interpreter'].llm.api_key = st.session_state['openrouter_key']
        st.session_state['interpreter'].llm.context_window = st.session_state['context_window']
    elif st.session_state['api_choice'] == 'openai':
        st.session_state['interpreter'].llm.api_key = st.session_state['openai_key']
        st.session_state['interpreter'].llm.context_window = st.session_state['context_window']
        st.session_state['interpreter'].llm.api_base = os.environ['OPENAI_API_BASE']
    elif st.session_state['api_choice'] == 'azure_openai':
        st.session_state['interpreter'].llm.api_key = st.session_state['openai_key']
        st.session_state['interpreter'].llm.api_base = st.session_state['azure_endpoint']
        st.session_state['interpreter'].llm.api_version = st.session_state['api_version']
    elif st.session_state['api_choice'] == 'vertexai':
        st.session_state['interpreter'].llm.context_window = st.session_state['context_window']
    elif st.session_state['api_choice'] == 'local':
        st.session_state['interpreter'].llm.context_window = st.session_state['context_window']
        st.session_state['interpreter'].offline = True
        if st.session_state['provider'] == 'Lmstudio':
            # Tells OI to send messages in OpenAI's format
            st.session_state['interpreter'].llm.model = "openai/x"
            # LiteLLM, which we use to talk to LM Studio, requires this
            st.session_state['interpreter'].llm.api_key = "fake_key"
            st.session_state['interpreter'].llm.api_base = st.session_state.get(
                'api_base')  # Point this at any OpenAI compatible server
        else:
            st.session_state[
                'interpreter'].llm.model = f"ollama_chat/{st.session_state.get('model')}"
            st.session_state['interpreter'].llm.api_base = st.session_state.get(
                'api_base')

    # Debug
    # st.write(interpreter.__dict__)
    # st.write(f'{interpreter.conversation_history_path=}')
    # st.write(f'{interpreter.conversation_filename =}')
    
def respond_to_query(query):
    lang = detect(query)
    
    if lang == 'tr':
        response = f"Bu sorguya Türkçe yanıt veriyorum: {query}"
    else:
        response = f"Responding in English: {query}"
    
    return response