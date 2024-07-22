import streamlit as st
import json
import re
import uuid
import platform
import os
from urllib.parse import urlparse, urljoin
from streamlit.components.v1 import html
from streamlit_extras.add_vertical_space import add_vertical_space

from st_components.st_conversations import conversation_navigation

INTERPRETER_DIR = os.path.join(os.getcwd(), 'interpreter')


def st_sidebar():

    with st.sidebar:
        
        file_handling()
        #about_us()


def about_us():
    add_vertical_space(4)
    st.markdown(
        f"<div style='text-align: center'><a href='https://cerebrumtechnologies.com/' target='_blank'><img src='https://cerebrumtechnologies.com/wp-content/uploads/2020/12/logo.png' width='200'></a></div>",
        unsafe_allow_html=True,
    )
    add_vertical_space(2)
    html_chat = '<center><h5>The CereAI Code Interpreter runs code on a sandbox environment connected to the Internet. Make sure to use it responsibly on production environments.</h5>'
    st.markdown(html_chat, unsafe_allow_html=True)


def file_handling():
    if not os.path.exists(INTERPRETER_DIR):
        try:
            os.makedirs(INTERPRETER_DIR)
        except PermissionError as e:
            st.error(f"Permission error: {e}")
            return

    with st.expander(label="Documents", expanded=(st.session_state.get('chat_ready', False))):
        st.markdown("<h4>Upload Files:</h4>", unsafe_allow_html=True)
        add_vertical_space(1)

        uploaded_files = st.file_uploader("Choose a file", accept_multiple_files=True)
        for uploaded_file in uploaded_files:
            file_path = os.path.join(INTERPRETER_DIR, uploaded_file.name)
            try:
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())
                st.success(f"Saved file: {uploaded_file.name}")
            except PermissionError as e:
                st.error(f"Permission error while saving file: {e}")
                continue

        add_vertical_space(2)
        st.markdown("<h4>Loaded Documents:</h4>", unsafe_allow_html=True)
        add_vertical_space(1)

        try:
            files = os.listdir(INTERPRETER_DIR)
        except PermissionError as e:
            st.error(f"Permission error while accessing directory: {e}")
            files = []

        for filename in files:
            st.write(filename)

        if not files:
            st.write('No files in the directory')
        else:
            if st.button("Delete All Files"):
                for filename in files:
                    try:
                        os.remove(os.path.join(INTERPRETER_DIR, filename))
                        st.success(f"{filename} has been deleted!")
                    except PermissionError as e:
                        st.error(f"Permission error while deleting file: {e}")

            st.markdown("<h4>Download Files:</h4>", unsafe_allow_html=True)
            add_vertical_space(1)
            file_to_download = st.selectbox("Select a file", files, key="download_selectbox")
            if file_to_download:
                try:
                    st.download_button(
                        label="Download file",
                        data=open(os.path.join(INTERPRETER_DIR, file_to_download), "rb").read(),
                        file_name=file_to_download,
                    )
                except PermissionError as e:
                    st.error(f"Permission error while opening file: {e}")