import streamlit as st
import folium
import datetime
import pandas as pd
from streamlit_folium import st_folium
from scripts.geo_utils import load_geodata, find_clicked_delegation
from scripts.data_utils import load_pluviometry
from scripts.dashboard import show_dashboard

# --- Configuration de la page ---
st.set_page_config(
    layout="wide",
    page_title="SmartSDGTunisia - Pluviométrie",
    page_icon="🌧️",
    initial_sidebar_state="expanded"
)


# 🎨 Palette de couleurs cohérente
COLORS = {
    "sky_blue": "#00B4D8",
    "mint_green": "#43AA8B",
    "vivid_orange": "#F8961E",
    "raspberry_pink": "#F15BB5",
    "soft_purple": "#9B5DE5",
    "light_gray": "#F0F0F0",
    "dark_blue": "#1A1A2E"
}

# --- CSS Personnalisé ---
st.markdown(f"""
<style>
    /* Style de la navbar */
    [data-testid="stHeader"] {{
        background-color: {COLORS['dark_blue']} !important;
        padding: 0;
    }}
    
    /* Texte blanc dans la sidebar */
    .stSidebar .css-1oe5cao {{
        color: white !important;
    }}
    
    /* Style global */
    .stApp {{
        background-color: {COLORS['light_gray']};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    /* Titres */
    h1, h2, h3, h4 {{
        color: {COLORS['dark_blue']};
        font-weight: 600;
    }}
    
    /* Cartes et sections */
    .card {{
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border-left: 4px solid {COLORS['sky_blue']};
        transition: all 0.3s ease;
    }}
    
    .card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }}
    
    .section-title {{
        color: {COLORS['dark_blue']};
        border-bottom: 2px solid {COLORS['vivid_orange']};
        padding-bottom: 8px;
        margin-bottom: 20px;
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['dark_blue']} !important;
    }}
    
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, {COLORS['dark_blue']}, #1E1E3C) !important;
        padding: 20px 15px !important;
    }}
    
    /* Widgets dans la sidebar */
    .stSidebar .stDateInput, 
    .stSidebar .stSelectbox,
    .stSidebar .stFileUploader {{
        background: rgba(255,255,255,0.95) !important;
        border-radius: 8px !important;
        padding: 8px !important;
        border: 1px solid {COLORS['light_gray']} !important;
    }}
    
    .stSidebar label {{
        color: white !important;
        font-weight: 400 !important;
    }}
    
    /* Boutons */
    .stButton>button {{
        background: {COLORS['vivid_orange']} !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }}
    
    .stButton>button:hover {{
        background: {COLORS['raspberry_pink']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }}
    
    /* Carte Folium container */
    .folium-map {{
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        border: 1px solid {COLORS['light_gray']} !important;
    }}
    
    /* Messages */
    .stSuccess, .stInfo, .stWarning, .stError {{
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }}
    
    /* Navbar personnalisée */
    .navbar {{
        display: flex;
        justify-content: space-around;
        background-color: {COLORS['dark_blue']};
        padding: 15px 0;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    
    .nav-item {{
        color: white !important;
        padding: 8px 20px;
        border-radius: 20px;
        transition: all 0.3s ease;
        text-decoration: none;
        font-weight: 500;
    }}
    
    .nav-item:hover {{
        background-color: {COLORS['sky_blue']};
        transform: translateY(-2px);
    }}
    
    .nav-item.active {{
        background-color: {COLORS['vivid_orange']};
        font-weight: bold;
    }}
</style>
""", unsafe_allow_html=True)

df_pluvio = ""

# --- Navbar Personnalisée ---
st.markdown("""
<div class="navbar">
    <a href="#" class="nav-item active">🏠 Accueil</a>
    <a href="#" class="nav-item">🌍 Thèmes ODD</a>
    <a href="#" class="nav-item">🌡️ Climat</a>
    <a href="#" class="nav-item">📊 Données</a>
    <a href="#" class="nav-item">ℹ️ À propos</a>
</div>
""", unsafe_allow_html=True)

# --- Chargement des données géographiques ---
gdf_gouv, gdf_del = load_geodata()

# --- Sidebar Redesign ---
with st.sidebar:
    # En-tête de la sidebar
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['soft_purple']}, {COLORS['sky_blue']});
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    ">
        <h2 style="color: white; margin: 0; font-weight: 700;">🌧️ PluvioMap TN</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
            Analyse interactive des précipitations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section Importation
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.95);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    ">
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            color: {COLORS['dark_blue']};
        ">
            <span style="
                background-color: {COLORS['vivid_orange']};
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 10px;
                font-size: 16px;
            ">📤</span>
            <h4 style="margin: 0; color: {COLORS['dark_blue']};">Importation des données</h4>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choisir un fichier CSV",
        type=['csv'],
        help="Format requis : Date, Station, Pluvio_du_jour",
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Période
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.95);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    ">
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            color: {COLORS['dark_blue']};
        ">
            <span style="
                background-color: {COLORS['vivid_orange']};
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 10px;
                font-size: 16px;
            ">📅</span>
            <h4 style="margin: 0; color: {COLORS['dark_blue']};">Période d'analyse</h4>
        </div>
    """, unsafe_allow_html=True)
    
    today = datetime.date.today()
    default_start = today.replace(month=1, day=1)
    default_end = today
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Date de début", value=default_start, key="date_start")
    with col2:
        end_date = st.date_input("Date de fin", value=default_end, key="date_end")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Visualisation
    st.markdown(f"""
    <div style="
        background: rgba(255,255,255,0.95);
        padding: 18px;
        border-radius: 12px;
        margin-bottom: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    ">
        <div style="
            display: flex;
            align-items: center;
            margin-bottom: 15px;
            color: {COLORS['dark_blue']};
        ">
            <span style="
                background-color: {COLORS['vivid_orange']};
                color: white;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                margin-right: 10px;
                font-size: 16px;
            ">📊</span>
            <h4 style="margin: 0; color: {COLORS['dark_blue']};">Options de visualisation</h4>
        </div>
    """, unsafe_allow_html=True)
    
    graph_type = st.selectbox(
        "Type de graphique",
        options=["Courbe", "Barres", "Carte thermique"],
        index=0,
        label_visibility="collapsed"
    )
    
    # Bouton d'analyse
    analyze_btn = st.button(
        "Lancer l'analyse",
        type="primary",
        use_container_width=True,
        help="Cliquez pour mettre à jour la visualisation"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Section Status
    if uploaded_file is not None:
        df_pluvio = load_pluviometry(uploaded_file)
        if df_pluvio is not None:
            df_pluvio = df_pluvio[
                (df_pluvio['Date'].dt.date >= start_date) &
                (df_pluvio['Date'].dt.date <= end_date)
            ]
            
            st.markdown(f"""
            <div style="
                background: {COLORS['mint_green']}15;
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid {COLORS['mint_green']};
                margin-top: 20px;
                color: {COLORS['dark_blue']};
            ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="
                        background-color: {COLORS['mint_green']};
                        color: white;
                        width: 25px;
                        height: 25px;
                        border-radius: 50%;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        margin-right: 10px;
                        font-size: 14px;
                    ">✓</span>
                    <strong style="font-size: 15px; color: {COLORS['dark_blue']};">Données chargées</strong>
                </div>
                <p style="margin: 5px 0 0 25px; font-size: 14px; color: {COLORS['dark_blue']};">
                    <strong>Enregistrements :</strong> {len(df_pluvio):,}
                </p>
                <p style="margin: 5px 0 0 25px; font-size: 14px; color: {COLORS['dark_blue']};">
                    <strong>Période :</strong> {start_date.strftime('%d/%m/%Y')} → {end_date.strftime('%d/%m/%Y')}
                </p>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.error("❌ Format de fichier invalide")

# --- Titre Principal ---
st.markdown(f"""
<div style="
    background: white;
    padding: 25px;
    border-radius: 12px;
    margin-bottom: 30px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
">
    <h1 style="
        color: {COLORS['dark_blue']};
        margin: 0;
        text-align: center;
        font-weight: 700;
    ">
        🇹🇳 SmartSDGTunisia - Pluviométrie
    </h1>
    <p style="
        color: {COLORS['dark_blue']}90;
        text-align: center;
        margin: 10px 0 0 0;
        font-size: 16px;
    ">
        Plateforme de visualisation des données pluviométriques tunisiennes
    </p>
</div>
""", unsafe_allow_html=True)

# --- Création de la carte Folium ---
m = folium.Map(
    location=[34, 9], 
    zoom_start=6, 
    tiles="cartodbpositron",
    width="100%",
    height="100%"
)

# Style des couches cohérent avec la palette
style_del = {
    'fillColor': COLORS['mint_green'],
    'color': COLORS['dark_blue'],
    'weight': 1.2,
    'fillOpacity': 0.6
}

style_gouv = {
    'fillColor': COLORS['sky_blue'],
    'color': COLORS['dark_blue'],
    'weight': 2,
    'fillOpacity': 0.3
}

# Couche Délégations
folium.GeoJson(
    gdf_del,
    name="Délégations",
    style_function=lambda x: style_del,
    tooltip=folium.GeoJsonTooltip(
        fields=['del_fr', 'gouv_fr'],
        aliases=["Délégation:", "Gouvernorat:"],
        style=f"""
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: white;
            color: {COLORS['dark_blue']};
            padding: 8px;
            border-radius: 4px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            font-size: 13px;
        """
    )
).add_to(m)

# Couche Gouvernorats
folium.GeoJson(
    gdf_gouv,
    name="Gouvernorats",
    style_function=lambda x: style_gouv,
    tooltip=folium.GeoJsonTooltip(
        fields=['gouv_fr'],
        aliases=["Gouvernorat:"],
        style=f"""
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: white;
            color: {COLORS['dark_blue']};
            padding: 8px;
            border-radius: 4px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
            font-size: 13px;
        """
    )
).add_to(m)

# Contrôle des layers
folium.LayerControl(collapsed=False, position='topright').add_to(m)

# --- Layout Principal ---
col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    st.markdown(f"<h2 class='section-title'>🗺️ Carte Interactive</h2>", unsafe_allow_html=True)
    map_data = st_folium(
        m, 
        height=700, 
        width="100%", 
        returned_objects=["last_object_clicked"]
    )

with col2:
    st.markdown(f"<h2 class='section-title'>📈 Dashboard</h2>", unsafe_allow_html=True)
    clicked_properties = None

    if map_data and "last_object_clicked" in map_data:
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
            st.info(f"📍 Gouvernorat sélectionné : {clicked_gouv['gouv_fr']}")
    
    if clicked_properties is None:
        show_dashboard(None, df_pluvio, graph_type)

# --- Pied de page ---
st.markdown(f"""
<div style="
    margin-top: 50px;
    padding: 15px;
    text-align: center;
    color: {COLORS['dark_blue']};
    font-size: 14px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
">
    © 2023 SmartSDGTunisia - Plateforme de suivi ODD<br>
    <span style="font-size: 12px; color: {COLORS['dark_blue']}80;">
        Données fournies par l'INS Tunisie et les partenaires techniques
    </span>
</div>
""", unsafe_allow_html=True)