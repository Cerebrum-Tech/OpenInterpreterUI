import streamlit as st
from st_components.st_interpreter import setup_interpreter
# Database
from src.data.database import save_chat
from src.data.models import Chat

# Image
from PIL import Image
from io import BytesIO
import base64

def chat_with_interpreter():
   
    if prompt := st.chat_input(placeholder="Write here your message", disabled=not st.session_state['chat_ready']):
        setup_interpreter()
        handle_user_message(prompt)
        handle_assistant_response(prompt)

def handle_user_message(prompt):
    with st.chat_message("user"):
        st.markdown(f'<p>{prompt}</p>', True)
        st.session_state.messages.append({"role": "user", "content": prompt})
        user_chat = Chat(st.session_state['current_conversation']["id"], "user", prompt)
        save_chat(user_chat)

def add_memory(prompt):
    look_back = -2 * st.session_state['num_pair_messages_recall']
    memory = '\n'.join([f"{i['role'].capitalize()}: {i['content']}" for i in st.session_state['messages'][look_back:]]).replace('User', '\nUser')
    prompt_with_memory = f"user's request:{prompt}. --- \nBelow is the transcript of your past conversation with the user: {memory} ---\n"
    return prompt_with_memory

def handle_assistant_response(prompt):
    with st.chat_message("assistant"):
        full_response = ""
        message_placeholder = st.empty()
        message = add_memory(prompt)
        with st.spinner('thinking'):
            for chunk in st.session_state['interpreter'].chat([{"role": "user", "type": "message", "content": message}], display=False, stream=True):
                full_response = format_response(chunk, full_response)
                message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        assistant_chat = Chat(st.session_state['current_conversation']["id"], "assistant", full_response)
        save_chat(assistant_chat)
        st.session_state['mensajes'] = st.session_state['interpreter'].messages

def format_response(chunk, full_response):
    if chunk['type'] == "message":
        full_response += chunk.get("content", "")
        if chunk.get('end', False):
            full_response += "\n"

    
    if chunk['type'] == "code" or chunk['type'] == "confirmation":
        return full_response

    if chunk['type'] == "console":
        if chunk.get('start', False):
            full_response += ""  
        if chunk.get('format', '') in ["active_line", "output"]:
            console_content = str(chunk.get('content', '')) 
            if console_content is None:
                full_response += "No output available on console."
            else:
                full_response += console_content
        if chunk.get('end', False):
            full_response += ""  

    if chunk['type'] == "image":
        if chunk.get('start', False) or chunk.get('end', False):
            full_response += "\n"
        else:
            image_format = chunk.get('format', '')
            if image_format == 'base64.png':
                image_content = chunk.get('content', '')
                if image_content:
                    image = Image.open(BytesIO(base64.b64decode(image_content)))
                    new_image = Image.new("RGB", image.size, "white")
                    new_image.paste(image, mask=image.split()[3])
                    buffered = BytesIO()
                    new_image.save(buffered, format="PNG")
                    img_str = base64.b64encode(buffered.getvalue()).decode()
                    full_response += f"![Image](data:image/png;base64,{img_str})\n"

    return full_response