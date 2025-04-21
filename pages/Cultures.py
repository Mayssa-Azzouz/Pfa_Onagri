import streamlit as st
import geopandas as gpd
import ssl
import urllib.request
from tempfile import NamedTemporaryFile
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Zones d'intervention ODESYPANO", layout="wide")

st.title("🌍 Zones d’intervention de l’ODESYPANO")

# Bypass SSL verification (temporairement)
ssl._create_default_https_context = ssl._create_unverified_context

# URL du fichier GeoJSON
geojson_url = "https://catalog.agridata.tn/dataset/205de34c-9c7d-497a-a6ce-b66db34a3f97/resource/cc21dad7-1f59-4680-914e-788dca2cc40a/download/z_interv_pno4.geojson"

@st.cache_data(show_spinner=True)
def load_geojson_from_url(url):
    with urllib.request.urlopen(url) as response:
        with NamedTemporaryFile(delete=False, suffix=".geojson") as tmp_file:
            tmp_file.write(response.read())
            return gpd.read_file(tmp_file.name)

# Chargement des données
gdf = load_geojson_from_url(geojson_url)

st.success("✅ Données chargées avec succès")

# Affichage des informations de base
st.subheader("Aperçu des données")

# Pour chaque ligne, afficher la description avec un rendu HTML
for index, row in gdf.iterrows():
    st.write(f"**Nom de la zone**: {row['Name']}")
    st.markdown(row['description'], unsafe_allow_html=True)
    st.write("\n---\n")

# Création d'une carte Folium
st.subheader("🗺️ Visualisation des zones sur la carte")
m = folium.Map(location=[34.5, 9.5], zoom_start=7)

# Ajout des zones depuis GeoJSON
folium.GeoJson(
    gdf,
    name="Zones ODESYPANO",
    tooltip=folium.GeoJsonTooltip(fields=gdf.columns[:2].tolist(), aliases=["Champ 1", "Champ 2"])
).add_to(m)

# Affichage avec streamlit-folium
st_folium(m, width=1200, height=600)

print(gdf.columns)
