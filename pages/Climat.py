import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Tableau de bord des précipitations", layout="wide")

st.title("🌧️ Tableau de bord des précipitations mensuelles")

# Chargement des données
@st.cache_data
def charger_donnees():
    df = pd.read_excel("Rainfall_data.xlsx", sheet_name="Data")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = charger_donnees()

# Sélection des stations
stations = df.columns[1:]
stations_selectionnees = st.multiselect("Sélectionnez une ou plusieurs stations :", stations, default=list(stations[:3]))

# Filtre de date
col1, col2 = st.columns(2)
with col1:
    date_min = st.date_input("Date de début :", df['Date'].min())
with col2:
    date_max = st.date_input("Date de fin :", df['Date'].max())

df_filtrée = df[(df["Date"] >= pd.to_datetime(date_min)) & (df["Date"] <= pd.to_datetime(date_max))]

# Vérification de sélection
if not stations_selectionnees:
    st.warning("Veuillez sélectionner au moins une station.")
    st.stop()

# Données transformées pour affichage graphique
df_melted = df_filtrée.melt(id_vars="Date", value_vars=stations_selectionnees, var_name="Station", value_name="Précipitations (mm)")

# Graphique temporel
st.subheader("📈 Évolution des précipitations")
fig = px.line(df_melted, x="Date", y="Précipitations (mm)", color="Station", markers=True)
fig.update_layout(xaxis_title="Date", yaxis_title="Précipitations (mm)")
st.plotly_chart(fig, use_container_width=True)

# Statistiques
st.subheader("📊 Statistiques par station")

df_stats = df_filtrée[["Date"] + stations_selectionnees].copy()
df_stats["Année"] = df_stats["Date"].dt.year
df_annuelle = df_stats.groupby("Année")[stations_selectionnees].agg(["mean", "sum"]).round(2)

st.dataframe(df_annuelle.style.format("{:.2f}").highlight_max(axis=0), use_container_width=True)
