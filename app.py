import streamlit as st
import folium
import datetime
from streamlit_folium import st_folium

# Local modules
from scripts.geo_utils import load_geodata, find_clicked_delegation
from scripts.data_utils import load_pluviometry
from scripts.dashboard import show_dashboard

# --- Page config
st.set_page_config(layout="wide", page_title="Carte Tunisie - Pluviométrie")
st.title("🇹🇳 Carte Interactive Tunisie - Données Pluviométriques")

# --- Load geographical data
gdf_gouv, gdf_del = load_geodata()

# --- Sidebar ---
st.sidebar.markdown("## 🌧️ PluvioMap TN")
# --- Sidebar: file uploader
st.sidebar.header("Importation des données")
uploaded_file = st.sidebar.file_uploader(
    "Importer le fichier pluviométrique (CSV)",
    type=['csv'],
    help="Le fichier doit contenir les colonnes: Date, station, Pluvio_du_jour, etc."
)

# Dates par défaut
today = datetime.date.today()
default_start = today.replace(month=1, day=1)
default_end = today

# --- Sélection de la période
start_date = st.sidebar.date_input("📅 Date de début", value=default_start)
end_date = st.sidebar.date_input("📅 Date de fin", value=default_end)

# --- Choix du type de graphique
graph_type = st.sidebar.selectbox(
    "📊 Choisir le type de graphique",
    options=["Courbe", "Barres"],
    index=0
)

df_pluvio = None
if uploaded_file is not None:
    df_pluvio = load_pluviometry(uploaded_file)
    if df_pluvio is not None:
        df_pluvio = df_pluvio[
            (df_pluvio['Date'].dt.date >= start_date) &
            (df_pluvio['Date'].dt.date <= end_date)
        ]
        st.sidebar.success("Fichier chargé avec succès!")
        st.sidebar.write(f"Nombre d'enregistrements: {len(df_pluvio)}")
        st.sidebar.write(f"Période filtrée: {start_date} ➡ {end_date}")

    else:
        st.sidebar.error("Erreur lors du chargement du fichier.")
else:
    st.sidebar.warning("Veuillez importer un fichier CSV")

# --- Create Folium map
m = folium.Map(location=[34, 9], zoom_start=6)
style = {'fillColor': '#3bdb6e', 'color': '#0c5e26', 'weight': 1, 'fillOpacity': 0.5}

# Add delegation layer
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

# --- Layout: map + dashboard
col1, col2 = st.columns([2, 1])

with col1:
    map_data = st_folium(m, height=700, width="100%", returned_objects=["last_object_clicked"])

with col2:
    clicked_properties = None
    if map_data and "last_object_clicked" in map_data:
        clicked_delegation = find_clicked_delegation(map_data["last_object_clicked"], gdf_del)
        if clicked_delegation is not None:
            clicked_properties = {
                'del_ar': clicked_delegation['del_ar'],
                'del_fr': clicked_delegation['del_fr'],
                'gouv_fr': clicked_delegation['gouv_fr']
            }

    # Show dashboard if a delegation is selected
    show_dashboard(clicked_properties, df_pluvio, graph_type)
