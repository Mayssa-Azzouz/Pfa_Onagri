import streamlit as st
import folium
import datetime
from streamlit_folium import st_folium

# Local modules
from scripts.geo_utils import load_geodata, find_clicked_delegation
from scripts.data_utils import load_pluviometry
from scripts.dashboard import show_dashboard

import streamlit as st

# --- Configuration de base ---
st.set_page_config(
    layout="wide",
    page_title="Carte Tunisie - Pluviométrie",
    page_icon="🌧️"
)

# --- CSS Responsive pour la Sidebar ---
st.markdown("""
    <style>
        /* Largeur par défaut (desktop) */
        section[data-testid="stSidebar"] {
            width: 280px !important;
            min-width: 280px !important;
        }
        
        /* Adaptation pour tablettes */
        @media (max-width: 992px) {
            section[data-testid="stSidebar"] {
                width: 240px !important;
                min-width: 240px !important;
            }
            .sidebar .sidebar-content {
                padding: 1rem !important;
            }
        }
        
        /* Adaptation pour mobiles */
        @media (max-width: 768px) {
            section[data-testid="stSidebar"] {
                width: 180px !important;
                min-width: 180px !important;
            }
            .sidebar .sidebar-content {
                padding: 0.5rem !important;
            }
            /* Simplification du texte pour petits écrans */
            .sidebar h2 {
                font-size: 1.1rem !important;
            }
            .sidebar .stFileUploader label {
                font-size: 0.8rem !important;
            }
        }
        
        /* Masquage optionnel sur très petits écrans */
        @media (max-width: 480px) {
            section[data-testid="stSidebar"] {
                transform: translateX(-100%);
                transition: transform 300ms;
                z-index: 100;
                position: fixed;
                height: 100vh;
                background: white;
            }
            section[data-testid="stSidebar"]:hover {
                transform: translateX(0);
            }
            /* Bouton pour afficher/masquer */
            .sidebar-toggle {
                display: block !important;
                position: fixed;
                left: 5px;
                top: 50%;
                z-index: 101;
                background: #1E90FF;
                color: white;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                text-align: center;
                line-height: 30px;
                cursor: pointer;
            }
        }
        
        /* Ajustements généraux du contenu */
        .sidebar .sidebar-content {
            transition: all 300ms ease;
            width: 100% !important;
        }
        .stDateInput, .stSelectbox, .stFileUploader {
            width: 100% !important;
        }
    </style>
    
    <!-- Bouton toggle pour mobile (optionnel) -->
    <div class="sidebar-toggle" onclick="toggleSidebar()">≡</div>
    <script>
        function toggleSidebar() {
            const sidebar = document.querySelector("section[data-testid='stSidebar']");
            const curr = sidebar.style.transform;
            sidebar.style.transform = curr === 'translateX(0px)' ? 'translateX(-100%)' : 'translateX(0px)';
        }
    </script>
""", unsafe_allow_html=True)

# --- Votre contenu existant ---
st.title("🇹🇳 Carte Interactive Tunisie - Données Pluviométriques")

with st.sidebar:
    st.markdown("## 🌧️ PluvioMap TN")
    # ... (le reste de votre contenu sidebar)

# --- Load geographical data
gdf_gouv, gdf_del = load_geodata()

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
        <div style='text-align: center;'>
            <h2 style='color: #1E90FF;'>🌧️ PluvioMap TN</h2>
            <p style='color: #555;'>Visualisation des données pluviométriques tunisiennes</p>
        </div>
    """, unsafe_allow_html=True)
    
    # --- Sidebar: file uploader
    st.header("📤 Importation des données")
    uploaded_file = st.file_uploader(
        "Importer le fichier pluviométrique (CSV)",
        type=['csv'],
        help="Le fichier doit contenir les colonnes: Date, station, Pluvio_du_jour, etc."
    )

    # Dates par défaut
    today = datetime.date.today()
    default_start = today.replace(month=1, day=1)
    default_end = today

    # --- Sélection de la période
    st.header("📅 Période d'analyse")
    start_date = st.date_input("Date de début", value=default_start)
    end_date = st.date_input("Date de fin", value=default_end)

    # --- Choix du type de graphique
    st.header("📊 Options de visualisation")
    graph_type = st.selectbox(
        "Type de graphique",
        options=["Courbe", "Barres"],
        index=0
    )

# Gestion des données
df_pluvio = None
if uploaded_file is not None:
    df_pluvio = load_pluviometry(uploaded_file)
    if df_pluvio is not None:
        df_pluvio = df_pluvio[
            (df_pluvio['Date'].dt.date >= start_date) &
            (df_pluvio['Date'].dt.date <= end_date)
        ]
        st.sidebar.success("✅ Fichier chargé avec succès!")
        st.sidebar.info(f"📊 Nombre d'enregistrements: {len(df_pluvio)}")
        st.sidebar.info(f"🗓️ Période filtrée: {start_date} ➡ {end_date}")
    else:
        st.sidebar.error("❌ Erreur lors du chargement du fichier.")
else:
    st.sidebar.warning("⚠️ Veuillez importer un fichier CSV")

# --- Create Folium map with better style
m = folium.Map(location=[34, 9], zoom_start=6, tiles="cartodbpositron")

# Style des couches
style_del = {'fillColor': '#3bdb6e', 'color': '#0c5e26', 'weight': 1, 'fillOpacity': 0.6}
style_gouv = {'fillColor': '#6495ED', 'color': '#1E90FF', 'weight': 2, 'fillOpacity': 0.4}

# --- Layer Délégations
folium.GeoJson(
    gdf_del,
    name="Délégations",
    style_function=lambda x: style_del,
    tooltip=folium.GeoJsonTooltip(
        fields=['del_fr', 'gouv_fr', 'del_ar'],
        aliases=["Délégation:", "Gouvernorat:", "Nom arabe:"],
        sticky=True,
        style=("background-color: white; color: #333; font-family: sans-serif;")
    )
).add_to(m)

# --- Layer Gouvernorats
folium.GeoJson(
    gdf_gouv,
    name="Gouvernorats",
    style_function=lambda x: style_gouv,
    tooltip=folium.GeoJsonTooltip(
        fields=['gouv_fr', 'gouv_ar'],
        aliases=["Gouvernorat (FR):", "Gouvernorat (AR):"],
        sticky=True,
        style=("background-color: white; color: #333; font-family: sans-serif;")
    )
).add_to(m)

# --- Ajouter le contrôle des layers
folium.LayerControl(collapsed=False).add_to(m)

# --- Layout: map + dashboard
col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    st.markdown("### 🗺️ Carte Interactive")
    map_data = st_folium(m, height=700, width="100%", returned_objects=["last_object_clicked"])

with col2:
    st.markdown("### 📈 Données Pluviométriques")
    clicked_properties = None

    if map_data and "last_object_clicked" in map_data:
        # Essayer d'abord la délégation
        clicked_delegation = find_clicked_delegation(map_data["last_object_clicked"], gdf_del)
        clicked_gouv = find_clicked_delegation(map_data["last_object_clicked"], gdf_gouv)

        if clicked_delegation is not None:
            clicked_properties = {
                'del_ar': clicked_delegation['del_ar'],
                'del_fr': clicked_delegation['del_fr'],
                'gouv_fr': clicked_delegation['gouv_fr']
            }
            show_dashboard(clicked_properties, df_pluvio, graph_type)

        elif clicked_gouv is not None:
            st.info(f"📍 Gouvernorat sélectionné : {clicked_gouv['gouv_fr']} / {clicked_gouv['gouv_ar']}")
    
    elif clicked_properties is None:
        show_dashboard(None, df_pluvio, graph_type)