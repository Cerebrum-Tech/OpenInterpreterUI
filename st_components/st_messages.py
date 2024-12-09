import streamlit as st
from st_components.st_interpreter import setup_interpreter
from src.data.database import save_chat
from src.data.models import Chat

from langdetect import detect, DetectorFactory, LangDetectException

from PIL import Image
from io import BytesIO
import base64


DetectorFactory.seed = 0

def detect_language(text):
    try:
        language = detect(text)
        return language
    except LangDetectException:
        return "unknown"

def chat_with_interpreter():
    if prompt := st.chat_input(placeholder="Write here your message", disabled=not st.session_state['chat_ready']):
        setup_interpreter()

        selected_language = st.session_state.get("selected_language", "en")
        language = detect_language(prompt)

        if language not in ["en", "tr"]:
            language = selected_language  

        handle_user_message(prompt)
        handle_assistant_response(prompt, selected_language)

def handle_user_message(prompt):
    with st.chat_message("user"):
        st.markdown(f'<p>{prompt}</p>', True)
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state['current_prompt'] = prompt 
        st.session_state['image_created'] = False    
        user_chat = Chat(
            st.session_state['current_conversation']["id"], "user", prompt)
        save_chat(user_chat)

def add_memory(prompt, language):
    look_back = -2 * st.session_state['num_pair_messages_recall']
    memory = '\n'.join(
        [f"{i['role'].capitalize()}: {i['content']}"
         for i in st.session_state['messages'][look_back:]]
    ).replace('User', '\nUser'
              )
    prompt_with_memory = f"user's request: {prompt}. Language: {language}. --- \nBelow is the transcript of your past conversation with the user: {memory} ---\n Yanıtı {language} olarak ver."
    return prompt_with_memory

def interpret_message(text):

    lang_code = detect_language(text)
    if lang_code == "tr":
        return "Türkçe"
    elif lang_code == "en":
        return "İngilizce"
    else:
        return "Bilinmiyor"

def handle_assistant_response(prompt, selected_language):
    with st.chat_message("assistant"):
        full_response = ""
        message_placeholder = st.empty()
        message = add_memory(prompt, selected_language)
        
        with st.spinner('thinking'):
            for chunk in st.session_state['interpreter'].chat(
                [{"role": "user", "type": "message", "content": message}], 
                display=False, 
                stream=True):
                full_response = format_response(chunk, full_response)
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)

        detected_lang = interpret_message(full_response)
        if not (selected_language == 'en' and detected_lang == "İngilizce") and not (
                selected_language == 'tr' and detected_lang == "Türkçe") and not (
                selected_language == 'fr' and detected_lang == "Fransızca") and not (
                selected_language == 'ko' and detected_lang == "Korece"):
            print(f"Yanıt beklenmeyen bir dilde geldi. Beklenen: {selected_language.capitalize()}, Gelen: {detected_lang}")

        st.session_state.messages.append(
            {"role": "assistant", "content": full_response})
        assistant_chat = Chat(
            st.session_state['current_conversation']["id"], "assistant", full_response)
        save_chat(assistant_chat)
        st.session_state['messages'] = st.session_state['interpreter'].messages

def format_response(chunk, full_response):
    show_code = st.session_state.get('show_code', False)

    if chunk['type'] == "message":
        content = chunk.get("content", "").replace(":\n", "\n").replace(": :", "")
        full_response += content

        if any(phrase in content for phrase in ["Step", "Plan", "Next Steps", "Summary", "Let's start", "I'll write a Python script", "plot using", "Next Steps", "proceed by",
                                                "Adım", "Plan", "Güncellenmiş Plan"]):
            return full_response

        if chunk.get('end', False):
            full_response += "\n"

    if show_code:
        if chunk['type'] == "code":
            if chunk.get('start', False):
                full_response += "```\n"
            full_response += chunk.get('content', '')
            if chunk.get('end', False):
                full_response += "\n```\n\n"

        if chunk['type'] == "console":
            if chunk.get('start', False):
                full_response += "```\n"
            if chunk.get('format', '') == "active_line":
                console_content = chunk.get('content', '')
                if console_content is None:
                    full_response += "No output available on console."
            if chunk.get('format', '') == "output":
                console_content = chunk.get('content', '')
                full_response += console_content
            if chunk.get('end', False):
                full_response += "\n```\n\n"

    if chunk['type'] == "image":
        
        if st.session_state.get('current_prompt') and not st.session_state.get('image_created', False):
            image_format = chunk.get('format', '')
            if image_format == "base64.png":
                image_content = chunk.get('content', '')
                if image_content:

                    try:
                        image = Image.open(BytesIO(base64.b64decode(image_content)))
                        new_image = Image.new("RGB", image.size, "white")
                        new_image.paste(image, mask=image.split()[3])
                        buffered = BytesIO()
                        new_image.save(buffered, format="PNG")
                        img_str = base64.b64encode(buffered.getvalue()).decode()
                        full_response += f"![Image](data:image/png;base64,{img_str})\n\n"
                        st.session_state['image_created'] = True  
                    except Exception as e:
                        st.error(f"Image processing error: {e}")
    return full_response

if __name__ == "_main_":
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'image_created' not in st.session_state:
        st.session_state['image_created'] = False

    chat_with_interpreter()

