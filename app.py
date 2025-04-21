import streamlit as st

# Configuration globale
st.set_page_config(
    page_title="SmartSDGTunisia",
    page_icon="🇹🇳",
    layout="wide"
)

# Tu peux aussi ajouter un message ou un redirigeur vers Accueil si tu veux
st.switch_page("pages/Accueil.py")  # Affiche la page d'accueil au démarrage
