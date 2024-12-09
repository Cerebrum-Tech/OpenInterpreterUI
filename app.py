import streamlit as st
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
import os
import sys

st.set_page_config(page_title="Open-Interpreter UI", page_icon="🤖", layout="wide")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'st_components')))


from st_settings import settings_page
from dashboard import show_dashboard
from dashboard_points import show_points_dashboard
from st_components.st_sidebar import st_sidebar
from st_components.st_main import st_main
from st_components.st_session_states import init_session_states
from st_components.st_dashboard import dashboard as wi_dashboard
from st_components.st_dashboard2 import dashboard2 as wi_dashboard2
from st_components.st_dashboard3 import dashboard3 as wi_dashboard3
from st_components.st_waterdashboard import water_dashboard as wi_water_dashboard
from st_components.st_askiDashboard import show_aski_panel
from st_components.st_init import set_style

# Load configuration
base_path = os.path.abspath(os.path.dirname(__file__))
config_file_path = os.path.join(base_path, 'config.yaml')
with open(config_file_path) as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(config['credentials'], config['cookie']['name'], config['cookie']['key'], config['cookie']['expiry_days'])

logo_url = "https://static.wixstatic.com/media/355375_f3c2f0e136f34270a3dd257007a3fee2~mv2.png/v1/fill/w_131,h_64,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/355375_f3c2f0e136f34270a3dd257007a3fee2~mv2.png"

def set_logo(selected_dashboard=None):
    global logo_url
    if selected_dashboard == 'Reengen':
        logo_url = "https://s3.eu-central-1.amazonaws.com/stajim/media/images/company/image/3507_20231130135121.jpg"
    elif selected_dashboard == 'WI.Plat':
        logo_url = "https://wiplat.com/wp-content/uploads/2023/10/wi_plat_logo_org.png"
    elif selected_dashboard == 'ASKİ':
        logo_url = "https://www.aski.gov.tr/Yukle/Resim/Icerik/logo-aski.png" 
    
    st.markdown(f"""
    <style>
        .header {{ display: flex; justify-content: center; align-items: center; flex-direction: column; margin-top: -100px; }}
        .header img {{ margin-bottom: 10px; }}
        .sidebar-content {{ display: flex; flex-direction: column; height: 100%; justify-content: flex-start; }}
        .sidebar-content .main-content {{ flex-grow: 1; }}
        .sidebar-content .logout {{ margin-bottom: 30px; }}
        .sidebar-buttons {{ display: flex; flex-direction: column; align-items: center; margin-top: 20px; }}
        .sidebar-buttons > * {{ width: 80%; margin-bottom: 10px; }}
        .sidebar-buttons button {{ border: 1px solid #ddd; }}
        .sidebar-buttons button:hover {{ background-color: #f0f0f0; }}
        .logout-btn {{ display: flex; align-items: center; justify-content: center; width: 100%; padding: 10px 0; font-size: 1em; border: 1px solid #e1e1e1; border-radius: 4px; cursor: pointer; color: #fff; background-color: transparent; text-align: center; }}
        .logout-btn:hover {{ background-color: #f0f0f0; color: #000; }}
        .logout-btn img {{ margin-left: 10px; width: 20px; }}
        .login-header {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            margin-top: 20px;  
            margin-bottom: 20px;
        }}
        .login-header img {{
            width: 150px;
            margin-bottom: 10px;
        }}
        .login-header .title {{
            font-size: 2.5em;
            font-weight: bold;
            text-align: center;
        }}
    </style>
    <div class="header">
        <img src="{logo_url}" alt="logo" width="150">
        <div style="font-size: 2.5em; font-weight: bold;">Cere Analytics</div>
    </div>
    """, unsafe_allow_html=True)

def main():
    init_session_states()
    login_placeholder = st.empty()

    try:
       login_result = authenticator.login('main', fields=["username", "password"])
       
       if login_result:  # Ensure it's not None
        name, authentication_status, username = login_result
       else:
        raise ValueError("Login failed, no values returned.")
    
    except Exception as e:
          st.error(f"Error during login: {e}")


    if authentication_status is None:
        with login_placeholder.container():
            st.markdown(f"""
            <style>
                .login-header {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    margin-top: 20px;  
                    margin-bottom: 20px;
                }}
                .login-header img {{
                    width: 150px;
                    margin-bottom: 10px;
                }}
                .login-header .title {{
                    font-size: 2.5em;
                    font-weight: bold;
                    text-align: center;
                }}
            </style>
            <div class="login-header">
                <img src="https://s3.eu-central-1.amazonaws.com/stajim/media/images/company/image/3507_20231130135121.jpg" alt="login logo">
                <div class="title">Cere Analytics</div>
            </div>
            """, unsafe_allow_html=True)

    if authentication_status:
        login_placeholder.empty()
        init_session_states()
        set_style()

        if 'page' not in st.session_state:
            st.session_state.page = 'Chat'

        st.sidebar.markdown('<div class="sidebar-content">', unsafe_allow_html=True)
        st.sidebar.markdown("<h2 style='text-align: center; margin-top: 5px;'>Select Option</h2>", unsafe_allow_html=True)
        st.sidebar.markdown('<div class="sidebar-buttons">', unsafe_allow_html=True)

        language_options = ['en', 'tr', 'fr', 'ko']
        if 'selected_language' not in st.session_state:
            st.session_state['selected_language'] = 'en'
        selected_language = st.sidebar.selectbox("Select Language", language_options, index=language_options.index(st.session_state['selected_language']))
        st.session_state['selected_language'] = selected_language

        page_options = ['Dashboard', 'Chat', 'Settings']
        selected_page = st.sidebar.selectbox("Select Page", page_options, index=page_options.index(st.session_state.page))

        if selected_page == 'Dashboard':
            dashboard_options = ['Reengen', 'WI.Plat', 'ASKİ']
            selected_dashboard = st.sidebar.selectbox("Select Dashboard", dashboard_options, index=dashboard_options.index('Reengen'))
            set_logo(selected_dashboard)

            if selected_dashboard == 'ASKİ':
                st.write('Hoşgeldin ASKİ')
            else:
                st.write(f'Welcome {selected_dashboard}')

            if selected_dashboard == 'Reengen':
                reengen_dashboard_option = st.sidebar.selectbox('Dashboard Options', ['Dashboard 1', 'Points Dashboard'])
                if reengen_dashboard_option == 'Dashboard 1':
                    show_dashboard()
                elif reengen_dashboard_option == 'Points Dashboard':
                    show_points_dashboard()

            elif selected_dashboard == 'WI.Plat':
                wi_plat_dashboard_option = st.sidebar.selectbox('WI.Plat Dashboard Options', ['Leak Investigation Dashboard', 'Leak Data Logging Dashboard', 'Leak Pinpointing Dashboard', 'Pressure Monitoring Dashboard'])
                if wi_plat_dashboard_option == 'Leak Investigation Dashboard':
                    wi_dashboard()
                elif wi_plat_dashboard_option == 'Leak Data Logging Dashboard':
                    wi_dashboard2()
                elif wi_plat_dashboard_option == 'Leak Pinpointing Dashboard':
                    wi_dashboard3()
                elif wi_plat_dashboard_option == 'Pressure Monitoring Dashboard':
                    wi_water_dashboard()

            elif selected_dashboard == 'ASKİ':
                aski_panel_option = st.sidebar.selectbox('ASKİ Dashboard Options', ['ASKİ Panel'])
                if aski_panel_option == 'ASKİ Panel':
                    show_aski_panel()

        elif selected_page == 'Chat':
            st.sidebar.markdown('</div>', unsafe_allow_html=True)
            st.write(f'Welcome *{name}*')
            st_sidebar()
            st_main()

        elif selected_page == 'Settings':
            st.sidebar.markdown('</div>', unsafe_allow_html=True)
            settings_page()

        st.session_state.page = selected_page

        st.sidebar.markdown('</div>', unsafe_allow_html=True)
        st.sidebar.markdown('<div style="flex-grow: 1;"></div>', unsafe_allow_html=True)
        st.sidebar.markdown('<div class="logout">', unsafe_allow_html=True)
        for _ in range(11):
            st.sidebar.markdown('<br>', unsafe_allow_html=True)
        authenticator.logout('Logout', 'sidebar')
        st.sidebar.markdown('</div>', unsafe_allow_html=True)

    elif authentication_status == False:
        st.error('Username/password is incorrect')
        with login_placeholder.container():
            st.markdown(f"""
            <style>
                .login-header {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    margin-top: 20px;
                    margin-bottom: 20px;
                }}
                .login-header img {{
                    width: 150px;
                    margin-bottom: 10px;
                }}
                .login-header .title {{
                    font-size: 2.5em;
                    font-weight: bold;
                    text-align: center;
                }}
            </style>
            <div class="login-header">
                <img src="https://s3.eu-central-1.amazonaws.com/stajim/media/images/company/image/3507_20231130135121.jpg" alt="login logo">
                <div class="title">Cere Analytics</div>
            </div>
            """, unsafe_allow_html=True)
    elif authentication_status is None:
        st.warning('Please enter your username and password')
        with login_placeholder.container():
            st.markdown(f"""
            <style>
                .login-header {{
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    margin-top: -20px;
                    margin-bottom: 20px;
                }}
                .login-header img {{
                    width: 150px;
                    margin-bottom: 10px;
                }}
                .login-header .title {{
                    font-size: 2.5em;
                    font-weight: bold;
                    text-align: center;
                }}
            </style>
            <div class="login-header">
                <img src="https://static.wixstatic.com/media/355375_f3c2f0e136f34270a3dd257007a3fee2~mv2.png/v1/fill/w_131,h_64,al_c,q_85,usm_0.66_1.00_0.01,enc_avif,quality_auto/355375_f3c2f0e136f34270a3dd257007a3fee2~mv2.png" alt="login logo">
                <div class="title">Cere Analytics</div>
            </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()