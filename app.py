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

# Style des couches
style_gouv = {
    'fillColor': '#3186cc',
    'color': '#000000',
    'weight': 2,
    'fillOpacity': 0.3
}

style_del = {
    'fillColor': '#e6550d',
    'color': '#636363',
    'weight': 1,
    'fillOpacity': 0.5,
    'dashArray': '5, 5'
}

# Couche Gouvernorats
folium.GeoJson(
    gdf_gouv,
    name="Gouvernorats",
    style_function=lambda x: style_gouv,
    tooltip=folium.GeoJsonTooltip(
        fields=['gouv_fr'],
        aliases=["Gouvernorat:"],
        sticky=True
    ),
    popup=folium.GeoJsonPopup(
        fields=['gouv_fr', 'gouv_id'],
        aliases=["Nom:", "Code:"]
    )
).add_to(m)

# Couche Délégations (visible via contrôle)
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
    st.subheader("Informations Administratives")
    
    # Affichage des infos selon ce qui est cliqué
    if clicked_data.get("last_object_clicked"):
        props = clicked_data["last_object_clicked"]["properties"]
        
        if 'del_fr' in props:  # Si délégation cliquée
            st.markdown(f"### 🏘 {props['del_fr']}")
            st.write(f"**Type:** Délégation")
            st.write(f"**Code:** {props['del_id']}")
            st.write(f"**Gouvernorat:** {props['gouv_fr']}")
            
            # Statistiques simulées
            st.divider()
            st.metric("Population", f"{np.random.randint(50000, 200000):,}")
            
        elif 'gouv_fr' in props:  # Si gouvernorat cliqué
            st.markdown(f"### 🏛 {props['gouv_fr']}")
            st.write(f"**Type:** Gouvernorat")
            st.write(f"**Code:** {props['gouv_id']}")
            
            # Délégations du gouvernorat
            delegations = gdf_del[gdf_del['gouv_id'] == props['gouv_id']]
            st.divider()
            st.markdown(f"**Délégations ({len(delegations)})**")
            for _, row in delegations.head(5).iterrows():
                st.write(f"- {row['del_fr']}")
            
            if len(delegations) > 5:
                st.write(f"... et {len(delegations)-5} autres")

# Options dans la sidebar
with st.sidebar:
    st.header("Options")
    if st.checkbox("Afficher toutes les délégations", False):
        folium.GeoJson(
            gdf_del,
            name="Délégations",
            style_function=lambda x: style_del
        ).add_to(m)
    
    if st.checkbox("Colorier par gouvernorat", True):
        # Palette de couleurs aléatoires
        colors = {gouv: f"#{np.random.randint(0, 0xFFFFFF):06x}" 
                 for gouv in gdf_gouv['gouv_fr'].unique()}
        
        def style_by_gouv(feature):
            gouv = feature['properties']['gouv_fr']
            return {
                'fillColor': colors.get(gouv, '#999999'),
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            }
        
        folium.GeoJson(
            gdf_gouv,
            style_function=style_by_gouv
        ).add_to(m)