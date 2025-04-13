import streamlit as st
import geopandas as gpd
import folium
from shapely.geometry import Point
from streamlit_folium import st_folium

# Configuration de Streamlit
st.set_page_config(layout="wide")
st.title("🌧️ Test Pluviométrique Statique - Tunisie")

# ---- Charger le fichier GeoJSON de délégations ----
@st.cache_data
def load_geojson():
    gdf = gpd.read_file("TN-delegations_raw.geojson")[['del_fr', 'gouv_fr', 'geometry']]
    return gdf

gdf_del = load_geojson()

# ---- Simuler des données statiques pour Djoumine (exemple) ----
static_data = {
    "Djoumine": {
        "Gouvernorat": "Bizerte",
        "Moyenne Pluvio (mm)": 17.8,
        "Max Pluvio (mm)": 32.5,
        "Cumul Mensuel (mm)": 103.2,
        "Nombre de jours de pluie": 11,
        "Tendance": [10, 12, 15, 20, 18, 25, 30, 22, 19, 24]
    },
    "Sejnane": {
        "Gouvernorat": "Bizerte",
        "Moyenne Pluvio (mm)": 14.2,
        "Max Pluvio (mm)": 28.1,
        "Cumul Mensuel (mm)": 88.6,
        "Nombre de jours de pluie": 9,
        "Tendance": [8, 10, 12, 13, 15, 20, 18, 19, 17, 16]
    }
}

# ---- Carte Folium ----
m = folium.Map(location=[37.2, 9.6], zoom_start=8)

def style_function(x):
    del_name = x['properties']['del_fr']
    # Si la délégation cliquée correspond à Djoumine, la colorer en rouge
    if del_name == "Djoumine":
        return {'fillColor': 'red', 'color': 'black', 'weight': 2, 'fillOpacity': 0.5}
    else:
        return {'fillColor': 'gray', 'color': 'black', 'weight': 1, 'fillOpacity': 0.2}

# Ajouter GeoJSON à la carte avec un tooltip
folium.GeoJson(
    gdf_del,
    name="Délégations",
    style_function=style_function,
    tooltip=folium.GeoJsonTooltip(fields=['del_fr', 'gouv_fr'], aliases=['Délégation:', 'Gouvernorat:']),
    # Ajouter un événement de clic pour capturer les coordonnées et le nom de la délégation
    highlight_function=lambda x: {'weight': 3, 'color': 'blue'},  # Accentuer lors du survol
).add_to(m)

# Layout de Streamlit (colonnes pour la carte et les données)
col1, col2 = st.columns([2, 1])

# Afficher la carte avec l'événement de clic
with col1:
    selected_location = st_folium(m, height=600, width="100%")

# Afficher les données associées à la délégation cliquée
with col2:
    if selected_location and "last_active_drawing" in selected_location:
        # Vérifier si des coordonnées ont été cliquées
        clicked_coords = selected_location.get("last_clicked", None)
        if clicked_coords:
            lat, lon = clicked_coords["lat"], clicked_coords["lng"]
            selected_delegation = None

            # Chercher si la délégation cliquée correspond à l'une des délégations de données statiques
            for feature in gdf_del.iterrows():
                feature = feature[1]
                # Récupérer la géométrie du polygone
                geom = feature['geometry']
                if geom.geom_type == 'Polygon':
                    polygon = geom
                    # Vérifier si le point est à l'intérieur du polygone
                    point = Point(lon, lat)
                    if polygon.contains(point):
                        selected_delegation = feature['del_fr']
                        break
                elif geom.geom_type == 'MultiPolygon':
                    # Si la géométrie est un MultiPolygon, utiliser .geoms pour itérer sur chaque polygone
                    for poly in geom.geoms:
                        point = Point(lon, lat)
                        if poly.contains(point):
                            selected_delegation = feature['del_fr']
                            break
                    if selected_delegation:
                        break

            if selected_delegation and selected_delegation in static_data:
                data = static_data[selected_delegation]
                st.subheader(f"📍 Données pour : {selected_delegation} ({data['Gouvernorat']})")
                st.metric("Pluviométrie Moyenne", f"{data['Moyenne Pluvio (mm)']} mm")
                st.metric("Pluie Maximale", f"{data['Max Pluvio (mm)']} mm")
                st.metric("Cumul du Mois", f"{data['Cumul Mensuel (mm)']} mm")
                st.metric("Jours de Pluie", f"{data['Nombre de jours de pluie']} jours")

                # Affichage de la tendance avec un graphique
                st.line_chart(data["Tendance"], use_container_width=True)
            else:
                st.info("Aucune donnée disponible pour cette délégation.")
        else:
            st.info("Cliquez sur une délégation pour voir les données.")
    else:
        st.write("Cliquez sur une délégation pour voir les données.")