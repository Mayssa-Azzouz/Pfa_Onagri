import pandas as pd
import streamlit as st

def load_pluviometry(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, parse_dates=['Date'])
        df['station'] = df['station'].str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {e}")
        return None
