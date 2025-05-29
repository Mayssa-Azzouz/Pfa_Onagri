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
    initial_sidebar_state="collapsed")

# 🎨 Palette de couleurs ONAGRI améliorée (version verte)
COLORS = {
    "primary_green": "#1E6C41",       # Vert foncé principal
    "dark_green": "#2E7D32",          # Vert plus doux pour navbar
    "light_green": "#78C27D",         # Vert clair
    "lighter_green": "#C8E6C9",       # Vert très clair
    "bg_green": "#F5FBF5",            # Fond vert très très clair
    "white": "#FFFFFF",
    "dark_text": "#263238",           # Texte foncé
    "light_text": "#607D8B",          # Texte secondaire
    "accent_orange": "#1E6C41",       # Orange plus vif
    "accent_blue": "#1976D2",         # Bleu pour complément
    "gradient_start": "#1E6C41",      # Début gradient
    "gradient_end": "#4CAF50"         # Fin gradient
}

# --- CSS Personnalisé ---
st.markdown(f"""
<style>
    /* Reset et styles de base */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    /* Masquer les éléments par défaut de Streamlit */
    header, footer {{
        visibility: hidden;
    }}
    
    #MainMenu {{
        display: none;
    }}
    
    /* Fix pour le z-index */
    section[data-testid="stSidebar"] {{
        z-index: 1001;
    }}
    
    /* Application principale */
    .stApp {{
        background-color: {COLORS['bg_green']};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: {COLORS['dark_text']};
        line-height: 1.6;
    }}
    
    /* Navigation modernisée */
    .navbar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(135deg, {COLORS['primary_green']}, {COLORS['dark_green']});
        padding: 0.8rem 0;
        z-index: 1000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        display: flex;
        justify-content: center;
    }}
    
    .nav-container {{
        display: flex;
        align-items: center;
        width: 100%;
        max-width: 1200px;
        padding: 0 1.5rem;
    }}
    
    .nav-brand {{
        color: {COLORS['white']};
        font-size: 1.5rem;
        font-weight: 700;
        margin-right: 2.5rem;
        display: flex;
        align-items: center;
    }}
    
    .nav-links {{
        display: flex;
        flex-grow: 1;
        justify-content: center;
        gap: 0.5rem;
        overflow-x: auto;
        scrollbar-width: none;
    }}
    
    .nav-links::-webkit-scrollbar {{
        display: none;
    }}
    
    .nav-link {{
        color: {COLORS['white']} !important;
        text-decoration: none !important;
        padding: 0.6rem 1.2rem;
        border-radius: 2rem;
        font-weight: 500;
        font-size: 0.95rem;
        transition: all 0.25s ease;
        white-space: nowrap;
        display: flex;
        align-items: center;
    }}
    
    .nav-link:hover {{
        background: rgba(255,255,255,0.15);
        transform: translateY(-2px);
    }}
    
    .nav-link.active {{
        background: {COLORS['primary_green']};
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    .nav-icon {{
        margin-right: 0.5rem;
        font-size: 1.1rem;
    }}
    
    /* Contenu principal */
    .main-content {{
        padding-top: 5rem;
        padding-bottom: 2rem;
    }}
    
    /* Ajustement de la position du contenu */
    .block-container {{
        padding-top: 100px;
    }}
    
    /* Titres */
    h1, h2, h3, h4 {{
        color: {COLORS['primary_green']};
        font-weight: 600;
    }}
    
    .section-title {{
        color: {COLORS['primary_green']};
        font-size: 1.8rem;
        font-weight: 600;
        margin: 30px 0 20px 0;
        position: relative;
        padding-bottom: 10px;
    }}
    
    .section-title:after {{
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 80px;
        height: 4px;
        background: linear-gradient(90deg, {COLORS['accent_orange']}, transparent);
        border-radius: 2px;
    }}
    
    /* Cartes modernes */
    .card {{
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        margin-bottom: 25px;
        transition: all 0.3s cubic-bezier(.25,.8,.25,1);
        border: none;
        height: 100%;
        display: flex;
        flex-direction: column;
    }}
    
    .card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    }}
    
    .card-title {{
        color: {COLORS['primary_green']};
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
    }}
    
    .card-icon {{
        margin-right: 10px;
        font-size: 1.4rem;
    }}
    
    .card-value {{
        font-size: 2.2rem;
        font-weight: 700;
        color: {COLORS['dark_text']};
        margin: 10px 0;
    }}
    
    .card-footer {{
        margin-top: auto;
        color: {COLORS['light_text']};
        font-size: 0.9rem;
    }}
    
    /* Sidebar améliorée */
    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, {COLORS['gradient_start']}, {COLORS['gradient_end']}) !important;
        padding: 20px !important;
    }}
    
    .sidebar-title {{
        color: white;
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 5px;
        text-align: center;
    }}
    
    .sidebar-subtitle {{
        color: rgba(255,255,255,0.9);
        font-size: 0.95rem;
        text-align: center;
        margin-bottom: 25px;
    }}
    
    .stSidebar .stSelectbox, 
    .stSidebar .stSlider,
    .stSidebar .stTextInput,
    .stSidebar .stDateInput,
    .stSidebar .stFileUploader {{
        background-color: rgba(255,255,255,0.9) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }}
    
    .stSidebar label {{
        color: white !important;
        font-weight: 500 !important;
    }}
    
    /* Boutons */
    .stButton>button {{
        background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_end']}) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        transition: all 0.3s !important;
    }}
    
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    }}
    
    /* Carte Folium container */
    .folium-map {{
        border-radius: 16px !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
        border: none !important;
        overflow: hidden;
    }}
    
    /* Messages */
    .stSuccess, .stInfo, .stWarning, .stError {{
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }}
    
    /* Conteneur KPI local */
    .local-kpi-container {{
        background: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }}
    
    .local-kpi-title {{
        color: {COLORS['primary_green']};
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }}
    
    .local-kpi-card {{
        background: {COLORS['lighter_green']};
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 15px;
        transition: all 0.3s;
    }}
    
    .local-kpi-card:hover {{
        background: {COLORS['light_green']};
        transform: translateX(5px);
    }}
    
    .local-kpi-label {{
        color: {COLORS['dark_text']};
        font-weight: 500;
        font-size: 0.95rem;
    }}
    
    .local-kpi-value {{
        color: {COLORS['primary_green']};
        font-weight: 700;
        font-size: 1.4rem;
        margin: 5px 0;
    }}
</style>
""", unsafe_allow_html=True)

# --- Barre de navigation personnalisée ---
def render_navbar(current="Pluviométrie"):
    """Barre de navigation modernisée"""
    st.markdown(f"""
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-brand">🌾 ONAGRI</div>
            <div class="nav-links">
                <a href="/" class="nav-link {'active' if current == 'Accueil' else ''}" target="_self">
                    <span class="nav-icon">🏠</span> Accueil
                </a>
                <a href="/Pluviometrie" class="nav-link {'active' if current == 'Pluviométrie' else ''}" target="_self">
                    <span class="nav-icon">🌧️</span> Pluviométrie
                </a>
                <a href="/rainfull_map" class="nav-link {'active' if current == 'Pluviométrie Région' else ''}" target="_self">
                    <span class="nav-icon">🌦️</span> Siliana/Kairouan
                </a>
                <a href="/Repartition_Biol" class="nav-link {'active' if current == 'Répartition Bio' else ''}" target="_self">
                    <span class="nav-icon">🧬</span> Biologique
                </a>
                <a href="/Eau_Portale" class="nav-link {'active' if current == 'Eau Potable' else ''}" target="_self">
                    <span class="nav-icon">💧</span> Eau Potable
                </a>
            </div>
        </div>
    </nav>
    <div class="main-content">
    """, unsafe_allow_html=True)

# --- Affichage de la navbar ---
render_navbar("Pluviométrie")

# --- Chargement des données géographiques ---
gdf_gouv, gdf_del = load_geodata()

# --- Sidebar Redesign ---
with st.sidebar:
    # En-tête de la sidebar
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_end']});
        padding: 25px 20px;
        border-radius: 16px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    ">
        <div class="sidebar-title">🌧️ PluvioMap TN</div>
        <div class="sidebar-subtitle">Analyse interactive des précipitations</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Section Importation
    st.markdown(f"""
    <div class="local-kpi-container">
        <div class="local-kpi-title">
            <span style="margin-right:10px;">📤</span> IMPORTATION DES DONNÉES
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
    <div class="local-kpi-container">
        <div class="local-kpi-title">
            <span style="margin-right:10px;">📅</span> PÉRIODE D'ANALYSE
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
    <div class="local-kpi-container">
        <div class="local-kpi-title">
            <span style="margin-right:10px;">📊</span> OPTIONS DE VISUALISATION
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
                background: {COLORS['light_green']}15;
                padding: 15px;
                border-radius: 10px;
                border-left: 4px solid {COLORS['light_green']};
                margin-top: 20px;
                color: {COLORS['dark_text']};
            ">
                <div style="display: flex; align-items: center; margin-bottom: 8px;">
                    <span style="
                        background-color: {COLORS['light_green']};
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
                    <strong style="font-size: 15px; color: {COLORS['dark_text']};">Données chargées</strong>
                </div>
                <p style="margin: 5px 0 0 25px; font-size: 14px; color: {COLORS['dark_text']};">
                    <strong>Enregistrements :</strong> {len(df_pluvio):,}
                </p>
                <p style="margin: 5px 0 0 25px; font-size: 14px; color: {COLORS['dark_text']};">
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
    border-radius: 16px;
    margin-bottom: 30px;
    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
">
    <h1 style="
        color: {COLORS['primary_green']};
        margin: 0;
        text-align: center;
        font-weight: 700;
    ">
        🇹🇳 SmartSDGTunisia - Pluviométrie
    </h1>
    <p style="
        color: {COLORS['light_text']};
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
    'fillColor': COLORS['light_green'],
    'color': COLORS['primary_green'],
    'weight': 1.2,
    'fillOpacity': 0.6
}

style_gouv = {
    'fillColor': COLORS['lighter_green'],
    'color': COLORS['primary_green'],
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
            color: {COLORS['primary_green']};
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
            color: {COLORS['primary_green']};
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
    color: {COLORS['light_text']};
    font-size: 14px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
">
    © 2023 SmartSDGTunisia - Plateforme de suivi ODD<br>
    <span style="font-size: 12px; color: {COLORS['light_text']}80;">
        Données fournies par l'INS Tunisie et les partenaires techniques
    </span>
</div>
""", unsafe_allow_html=True)

# Fermeture de la div main-content
st.markdown("</div>", unsafe_allow_html=True)