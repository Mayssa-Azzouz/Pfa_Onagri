import streamlit as st
import pandas as pd
from io import BytesIO
import ssl
import urllib.request
import plotly.express as px

st.set_page_config(page_title="Répartition du Cheptel", layout="wide")

st.title("🐄 Répartition du Cheptel en Tunisie")
st.markdown("Données issues de [Agridata.tn](https://catalog.agridata.tn/fr/dataset/repartition-du-cheptel)")

# Fonction pour charger le fichier Excel en ligne en contournant le SSL
@st.cache_data(show_spinner=True)
def load_data(url):
    ssl._create_default_https_context = ssl._create_unverified_context
    with urllib.request.urlopen(url) as response:
        data = response.read()
        return pd.read_excel(BytesIO(data))

# URL directe vers le fichier Excel
excel_url = "https://catalog.agridata.tn/dataset/50049b47-d86a-41a6-863c-a0c407e6ffbf/resource/990e744a-9c63-43ef-b57c-7726b50d5a76/download/elevage-tozeur-1.xlsx"

# Chargement des données
df = load_data(excel_url)

st.success("✅ Données chargées avec succès.")

# Affichage de l’aperçu des données
st.subheader("📊 Aperçu des données")
st.dataframe(df.head(), use_container_width=True)

# Nettoyage si nécessaire (à adapter selon structure exacte)
if "Gouvernorat" in df.columns:
    st.subheader("📈 Visualisation du cheptel par gouvernorat")

    col_to_plot = st.selectbox("📌 Choisir un type de cheptel à visualiser :", 
                               options=[col for col in df.columns if col != "Gouvernorat"])

    fig = px.bar(df, x="Gouvernorat", y=col_to_plot, color="Gouvernorat",
                 labels={"Gouvernorat": "Gouvernorat", col_to_plot: "Nombre"},
                 title=f"Répartition de {col_to_plot} par gouvernorat")
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("❗ La colonne 'Gouvernorat' n’a pas été trouvée. Veuillez vérifier la structure du fichier.")
