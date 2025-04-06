import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
import numpy as np

# Configuration de la page
st.set_page_config(layout="wide")
st.title("🇹🇳 Carte Interactive Tunisie - Gouvernorats & Délégations")

# Chargement des données
@st.cache_data
def load_data():
    # Gouvernorats
    gdf_gouv = gpd.read_file("TN-gouvernorats.geojson")
    
    # Délégations
    gdf_del = gpd.read_file("TN-delegations_raw.geojson")
    
    # Vérification des colonnes
    required_gouv = ['gouv_fr', 'gouv_id', 'geometry']
    required_del = ['del_fr', 'del_id', 'gouv_id', 'geometry']
    
    for col in required_gouv:
        if col not in gdf_gouv.columns:
            st.error(f"Colonne manquante dans gouvernorats: {col}")
            return None, None
            
    for col in required_del:
        if col not in gdf_del.columns:
            st.error(f"Colonne manquante dans délégations: {col}")
            return None, None
            
    return gdf_gouv, gdf_del

gdf_gouv, gdf_del = load_data()

if gdf_gouv is None or gdf_del is None:
    st.stop()

# Création de la carte
m = folium.Map(location=[34, 9], zoom_start=6)

# Style des couches
style_gouv = {
    'fillColor': '#3186cc',
    'color': '#000000',
    'weight': 2,
    'fillOpacity': 0.3
}

style_del = {
    'fillColor': '#3bdb6e',
    'color': '#0c5e26',
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
    style_function=lambda x: style_del,
    tooltip=folium.GeoJsonTooltip(
        fields=['del_fr', 'gouv_fr'],
        aliases=["Délégation:", "Gouvernorat:"],
        sticky=True
    ),
    control=False
).add_to(m)

# Contrôles de la carte
folium.LayerControl().add_to(m)

# Interface
col1, col2 = st.columns([2, 1])

with col1:
    # Affichage carte
    clicked_data = st_folium(
        m,
        height=700,
        width="100%",
        returned_objects=["last_object_clicked", "last_active_drawing"]
    )

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