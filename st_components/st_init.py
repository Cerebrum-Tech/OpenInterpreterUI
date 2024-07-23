# st_init.py
import streamlit as st


def set_page_config():
    st.set_page_config(
        page_title="Open-Interpreter UI",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

def set_style():    
    # STYLES
    st.markdown(
    """<style>.eczjsme4 {
            padding: 4rem 1rem;
            }
            .css-w770g5{
            width: 100%;}
            .css-b3z5c9{
            width: 100%;}
            .stButton>button{
            width: 100%;}
            .stDownloadButton>button{
            width: 100%;}
            button[data-testid="baseButton-primary"]{
            border-color: #505050;
            background-color: #1E1E1E;
            }
            button[data-testid="baseButton-primary"]:hover {
            border-color: #FC625F;
            background-color: #1E1E1E;
            color: #FC625F;
            }
            </style>""", 
        unsafe_allow_html=True
    )