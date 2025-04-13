import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from shapely.geometry import Point
import os

# --- Configuration de la page
st.set_page_config(layout="wide", page_title="Carte Tunisie - Pluviométrie")
st.title("🇹🇳 Carte Interactive Tunisie - Données Pluviométriques")

# --- Chargement des données géographiques
@st.cache_data
def load_geodata():
    gdf_gouv = gpd.read_file("TN-gouvernorats.geojson")
    gdf_del = gpd.read_file("TN-delegations_raw.geojson")
    return gdf_gouv, gdf_del

gdf_gouv, gdf_del = load_geodata()

# --- Gestion du fichier pluviométrique
def load_pluviometry(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file, parse_dates=['Date'])
        df['station'] = df['station'].str.strip()
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier: {e}")
        return None

# --- Fonction pour trouver la délégation cliquée
def find_clicked_delegation(click_coords, gdf):
    if not click_coords or 'lat' not in click_coords or 'lng' not in click_coords:
        return None
    
    point = Point(click_coords['lng'], click_coords['lat'])
    for idx, row in gdf.iterrows():
        if row['geometry'].contains(point):
            return row
    return None

# --- Fonction de normalisation arabe
def normalize_arabic(text):
    try:
        return get_display(reshape(text.strip())) if isinstance(text, str) else text
    except:
        return text

# --- Tableau de bord pluviométrique
def show_dashboard(properties, df):
    if not properties or df is None:
        st.info("Cliquez sur une délégation pour afficher les données")
        return
    
    del_ar = properties.get('del_ar')
    del_fr = properties.get('del_fr', 'Inconnu')
    
    st.markdown(f"### 📊 Données pour: {del_fr} / {del_ar}")
    
    # Normalisation et recherche des données
    normalized_del = normalize_arabic(del_ar)
    matching_stations = []
    
    for station in df['station'].unique():
        if normalize_arabic(station) == normalized_del:
            matching_stations.append(station)
    
    if not matching_stations:
        st.warning(f"Aucune station ne correspond à {del_ar}")
        return
    
    station_data = df[df['station'].isin(matching_stations)]
    
    if station_data.empty:
        st.warning("Données pluviométriques non disponibles")
        return
    
    # Affichage des données
    latest = station_data.iloc[-1]
    
    cols = st.columns(3)
    cols[0].metric("Pluie du jour", f"{latest['Pluvio_du_jour']} mm")
    cols[1].metric("Cumul mensuel", f"{latest['Cumul_du_mois']} mm")
    cols[2].metric("Cumul période", f"{latest['Cumul_periode']} mm")
    
    fig = px.line(station_data, x='Date', y='Pluvio_du_jour', 
                 title=f"Pluviométrie à {del_fr}")
    st.plotly_chart(fig, use_container_width=True)
    
    st.dataframe(station_data.sort_values('Date', ascending=False))

# --- Interface pour l'import du fichier
st.sidebar.header("Importation des données")
uploaded_file = st.sidebar.file_uploader("Importer le fichier pluviométrique (CSV)", 
                                        type=['csv'],
                                        help="Le fichier doit contenir les colonnes: Date, station, Pluvio_du_jour, etc.")

df_pluvio = None
if uploaded_file is not None:
    df_pluvio = load_pluviometry(uploaded_file)
    if df_pluvio is not None:
        st.sidebar.success("Fichier chargé avec succès!")
        st.sidebar.write(f"Nombre d'enregistrements: {len(df_pluvio)}")
        st.sidebar.write(f"Période couverte: {df_pluvio['Date'].min().date()} au {df_pluvio['Date'].max().date()}")
else:
    st.sidebar.warning("Veuillez importer un fichier CSV")

# --- Création de la carte
m = folium.Map(location=[34, 9], zoom_start=6)

# Style des délégations
style = {'fillColor': '#3bdb6e', 'color': '#0c5e26', 'weight': 1, 'fillOpacity': 0.5}

# Ajout des couches avec popup
folium.GeoJson(
    gdf_del,
    name="Délégations",
    style_function=lambda x: style,
    tooltip=folium.GeoJsonTooltip(
        fields=['del_fr', 'gouv_fr', 'del_ar'],
        aliases=["Délégation:", "Gouvernorat:", "Nom arabe:"],
        sticky=True
    )
).add_to(m)

# --- Interface principale
col1, col2 = st.columns([2, 1])

with col1:
    map_data = st_folium(
        m,
        height=700,
        width="100%",
        returned_objects=["last_object_clicked"]
    )

with col2:
    clicked_properties = None
    
    if map_data and "last_object_clicked" in map_data:
        # Trouver la délégation cliquée
        clicked_delegation = find_clicked_delegation(
            map_data["last_object_clicked"],
            gdf_del
        )
        
        if clicked_delegation is not None:
            clicked_properties = {
                'del_ar': clicked_delegation['del_ar'],
                'del_fr': clicked_delegation['del_fr'],
                'gouv_fr': clicked_delegation['gouv_fr']
            }
    
    show_dashboard(clicked_properties, df_pluvio)