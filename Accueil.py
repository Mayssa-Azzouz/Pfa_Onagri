import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page - MUST come first
st.set_page_config(
    page_title="SmartSDGTunisia", 
    page_icon="🇹🇳", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 🎨 Palette de couleurs Nature
COLORS = {
    "primary_green": "#2E8B57",
    "dark_green": "#1A5D1A",
    "light_green": "#90EE90",
    "lime_green": "#32CD32",
    "mint_green": "#98FB98",
    "olive_green": "#6B8E23",
    "white": "#FFFFFF",
    "light_gray": "#F5F5F5"
}

st.markdown(f"""
<style>
    /* Masquer les éléments par défaut de Streamlit */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}
    
    section[data-testid="stSidebar"] {{
        z-index: 1001;
        background-color: {COLORS['dark_green']} !important;
    }}
    
    .block-container {{
        padding-top: 100px;
    }}
    
    .stApp {{
        background-color: {COLORS['light_gray']};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* NAVBAR personnalisée */
    .main-nav {{
        position: fixed;
        top: 0;
        left: 0;
        height: 60px;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: space-around;
        background-color: {COLORS['dark_green']};
        padding: 0 10px;
        z-index: 1002;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}

    .nav-item {{
        color: {COLORS['white']} !important;
        padding: 8px 20px;
        border-radius: 20px;
        text-decoration: none;
        font-weight: 500;
        transition: all 0.3s ease;
        margin: 0 5px;
    }}

    .nav-item:hover {{
        background-color: {COLORS['primary_green']};
        transform: translateY(-2px);
    }}

    .nav-item.active {{
        background-color: {COLORS['lime_green']};
        color: {COLORS['dark_green']} !important;
        font-weight: 600;
    }}
</style>
""", unsafe_allow_html=True)


# Import and render navbar AFTER set_page_config
from components.navbar import render_navbar
render_navbar("Accueil")

# Your custom header (consider integrating this into your navbar component)
st.markdown("""
    <div style="background-color:#1A1A2E;padding:10px 20px;border-radius:0px;margin-bottom:20px">
        <h1 style="color:white;text-align:left;">📊 Smart Dashboard</h1>
    </div>
""", unsafe_allow_html=True)

# Rest of your page content...