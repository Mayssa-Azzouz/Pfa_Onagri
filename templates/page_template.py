# templates/page_template.py
import streamlit as st
from components.navbar import render_navbar
from config import COLORS, SIDEBAR_HEADER_STYLE

def base_layout(page_title, page_icon, current_page):
    st.set_page_config(
        layout="wide",
        page_title=f"SmartSDGTunisia - {page_title}",
        page_icon=page_icon,
        initial_sidebar_state="expanded"
    )
    
    # Applique la navbar verte
    render_navbar(current_page)
    
    # CSS global
    st.markdown(f"""
    <style>
        header, footer {{ visibility: hidden; }}
        #MainMenu {{ display: none; }}
        .block-container {{ padding-top: 80px; }}
        .stApp {{ background-color: {COLORS['background']}; }}
        h1, h2, h3, h4 {{ color: {COLORS['text_dark']}; }}
    </style>
    """, unsafe_allow_html=True)

def sidebar_header(title, description):
    with st.sidebar:
        st.markdown(SIDEBAR_HEADER_STYLE + f"""
            <h2 style="margin: 0; font-weight: 700;">{title}</h2>
            <p style="margin: 5px 0 0 0; font-size: 14px;">{description}</p>
        </div>
        """, unsafe_allow_html=True)