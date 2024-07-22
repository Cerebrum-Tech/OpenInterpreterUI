import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import os

st.set_page_config(
    page_title="Open-Interpreter UI",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

logo_url = "https://cerebrumtechnologies.com/wp-content/uploads/2020/12/logo.png"


st.markdown(
    f"""
    <style>
    .header {{
        display: flex;    
        justify-content: center;
        align-items: center;
        flex-direction: column;
        margin-top: 10px;
    }}
    .header img {{
        margin-bottom: 10px;
    }}
    .sidebar-content {{
        display: flex;
        flex-direction: column;
        height: 100%;
        justify-content: flex-start;
    }}
    .sidebar-content .main-content {{
        flex-grow: 1;
    }}
    .sidebar-content .logout {{
        margin-bottom: 30px; 
    }}
    .sidebar-buttons {{
        display: flex;
        flex-direction: column;
        align-items: center;
        margin-top: 20px;
    }}
    .sidebar-buttons > * {{
        width: 80%; 
        margin-bottom: 10px;
    }}
    </style>
    <div class="header">
        <img src="{logo_url}" alt="logo" width="150">
        <div style="font-size: 2.5em; font-weight: bold;">CereAI Code Interpreter</div>
    </div>
    """,
    unsafe_allow_html=True
)

from st_components.st_init import set_style
from st_components.st_session_states import init_session_states
from st_components.st_sidebar import st_sidebar
from st_components.st_main import st_main

import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from st_settings import settings_page

base_path = os.path.abspath(os.path.dirname(__file__))
config_file_path = os.path.join(base_path, 'config.yaml')
with open(config_file_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

def main():
    try:
        name, authentication_status, username = authenticator.login('main', fields=["username", "password"])
    except Exception as e:
        st.error(f"Error during login: {e}")

    if authentication_status:
        set_style()
        init_session_states()

        st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        #st.sidebar.markdown('<div class="main-content">', unsafe_allow_html=True)

        st.sidebar.markdown("<h2 style='text-align: center; margin-top: 5px;'>Select Option</h2>", unsafe_allow_html=True)
        
        
        st.sidebar.markdown('<div class="sidebar-buttons">', unsafe_allow_html=True)
        
        st.write(f'Welcome *{name}*')

        if st.sidebar.button('Chat'):
            st.session_state.page = 'Chat'
        if st.sidebar.button('Settings'):
            st.session_state.page = 'Settings'

        st.sidebar.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.get('page') == 'Settings':
            settings_page()
        else:
            st.session_state.page = 'Chat'
            st_sidebar()
            st_main()

        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        st.sidebar.markdown('<div style="flex-grow: 1;"></div>', unsafe_allow_html=True)  
        st.sidebar.markdown('<div class="logout">', unsafe_allow_html=True)
        for _ in range(11):  
            st.sidebar.markdown('<br>', unsafe_allow_html=True)
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

        

    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')

if __name__ == "__main__":
    main()