import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
from scripts.geo_utils import load_geodata, find_clicked_delegation
from scripts.data_utils import load_pluviometry

# Configuration de la page
st.set_page_config(
    layout="wide",
    page_title="ONAGRI Dashboard",
    page_icon="🌱",
    initial_sidebar_state="collapsed"
)

# 🎨 Palette de couleurs optimisée
COLORS = {
    "primary": "#1E6C41",      # Vert foncé
    "secondary": "#2E7D32",    # Vert
    "accent": "#4CAF50",       # Vert clair
    "background": "#F5FBF5",   # Fond très clair
    "text": "#263238",         # Texte foncé
    "white": "#FFFFFF"
}

# =============================================
# SECTION CSS PERSONNALISÉ
# =============================================
st.markdown(f"""
<style>
    /* Réinitialisation et base */
    * {{
        margin: 0;
        padding: 0;
        box-sizing: border-box;
    }}
    
    /* Application principale */
    .stApp {{
        background-color: {COLORS['background']};
        font-family: 'Segoe UI', Tahoma, sans-serif;
        color: {COLORS['text']};
        line-height: 1.6;
    }}
    
    /* Navigation modernisée */
    .navbar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']});
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
        background: {COLORS['primary']};
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    
    .nav-icon {{
        margin-right: 0.5rem;
        font-size: 1.1rem;
    }}
    
    /* Contenu principal */
    .main-content {{
        padding-top: 0rem;
        padding-bottom: -1rem;
    }}
    
    /* Cartes thématiques améliorées */
    .theme-card {{
        background: {COLORS['white']};
        border-radius: 1rem;
        padding: 1.75rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        transition: all 0.3s cubic-bezier(0.25,0.8,0.25,1);
        border-left: 5px solid {COLORS['primary']};
        cursor: pointer;
        height: 100%;
    }}
    
    .theme-card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 12px 24px rgba(0,0,0,0.12);
    }}
    
    /* En-têtes de section */
    .section-header {{
        background: linear-gradient(to right, {COLORS['primary']}, {COLORS['secondary']});
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        text-align: center;
    }}
    
    .section-header h1 {{
        color: {COLORS['white']} !important;
        font-size: 2.2rem;
        font-weight: 700;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
    }}
    
    /* Carte Folium */
    .folium-container {{
        border-radius: 1rem;
        overflow: hidden;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }}
    
    /* Style du sidebar simplifié */
    [data-testid="stSidebar"] {{
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']}) !important;
        padding: 1.5rem !important;
    }}
    
    /* Texte dans le sidebar */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] label {{
        color: {COLORS['white']} !important;
    }}
    
    /* Widgets dans le sidebar */
    [data-testid="stSidebar"] .stSelectbox,
    [data-testid="stSidebar"] .stSlider,
    [data-testid="stSidebar"] .stTextInput,
    [data-testid="stSidebar"] .stNumberInput,
    [data-testid="stSidebar"] .stRadio {{
        background-color: {COLORS['white']} !important;
        color: {COLORS['text']} !important;
    }}
    
    [data-testid="stSidebar"] .st-bb {{
        background-color: {COLORS['white']};
    }}
    
    [data-testid="stSidebar"] .st-at {{
        background-color: {COLORS['primary']};
    }}
    
    /* Boutons dans le sidebar */
    [data-testid="stSidebar"] .stButton button {{
        background-color: {COLORS['white']} !important;
        color: {COLORS['primary']} !important;
        border: 1px solid {COLORS['white']} !important;
    }}
    
    [data-testid="stSidebar"] .stButton button:hover {{
        background-color: {COLORS['accent']} !important;
        color: {COLORS['white']} !important;
    }}
    
    /* Masquer les éléments Streamlit */
    #MainMenu, footer, header {{
        visibility: hidden;
    }}
    
    /* Ajustements responsive */
    @media (max-width: 768px) {{
        .nav-container {{
            flex-direction: column;
            padding: 0.5rem;
        }}
        
        .nav-brand {{
            margin-right: 0;
            margin-bottom: 0.5rem;
        }}
        
        .nav-links {{
            flex-wrap: wrap;
        }}
        
        .nav-link {{
            padding: 0.5rem 1rem;
            font-size: 0.9rem;
        }}
        
        [data-testid="stSidebar"] {{
            padding: 0.5rem !important;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# =============================================
# COMPOSANTS DE L'INTERFACE
# =============================================

def render_navbar(current="Accueil"):
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
                <a href="/rainfall_map" class="nav-link {'active' if current == 'Pluviométrie Région' else ''}" target="_self">
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

def theme_card(icon, title, description, page):
    """Carte thématique cliquable"""
    st.markdown(f"""
    <a href="/{page}" style="text-decoration:none; color:inherit;" target="_self">
        <div class="theme-card">
            <h3 style="color:{COLORS['primary']}; font-size:1.4rem; margin-bottom:1rem;">
                {icon} {title}
            </h3>
            <p style="color:#555; font-size:1rem; margin-bottom:1.5rem;">{description}</p>
            <div style="text-align:right;">
                <span style="color:{COLORS['primary']}; font-weight:600;">Explorer →</span>
            </div>
        </div>
    </a>
    """, unsafe_allow_html=True)

# =============================================
# PAGES DE L'APPLICATION
# =============================================

def home_page():
    """Page d'accueil"""
    with st.sidebar:
        st.write("**Navigation rapide**")
        selected_page = st.radio(
            "Sections",
            ["Accueil", "Pluviométrie", "Pluviométrie Région", "Biologique", "Eau Potable"],
            index=0,
            label_visibility="collapsed"
        )
        
        st.write("---")
        st.write("**Filtres généraux**")
        year_filter = st.slider("Année", 2010, 2023, 2022)
        region_filter = st.selectbox("Région", ["Toutes", "Nord", "Centre", "Sud"])
    
    st.markdown(f"""
    <div style="text-align:center; margin-bottom:1rem;">
        <h1 style="color:{COLORS['primary']}; font-size:2.5rem; margin-bottom:0.5rem;">
            Tableau de Bord Agricole
        </h1>
        <p style="font-size:1.2rem; color:#555;">
            Plateforme de visualisation des données agricoles tunisiennes
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(2)
    with cols[0]:
        theme_card("🌧️", "Pluviométrie Nationale", 
                 "Analyse spatiale des précipitations sur toute la Tunisie", 
                 "Pluviometrie")
        theme_card("🌦️", "Pluviométrie Régionale", 
                 "Données détaillées pour les régions de Siliana et Kairouan", 
                 "rainfull_map")
    with cols[1]:
        theme_card("🧬", "Répartition Biologique", 
                 "Exploration de la biodiversité agricole par région", 
                 "Repartition_Biol")
        theme_card("💧", "Ressources en Eau", 
                 "Suivi des indicateurs de distribution d'eau potable", 
                 "Eau_Portale")

def pluviometrie_page():
    """Page pluviométrie nationale"""
    with st.sidebar:
        st.write("**Filtres Pluviométrie**")
        year = st.slider("Année", 2010, 2023, 2022, label_visibility="collapsed")
        season = st.selectbox("Saison", ["Toute l'année", "Hiver", "Printemps", "Été", "Automne"])
        show_table = st.checkbox("Afficher les données brutes", True)
    
    st.markdown("""
    <div class="section-header">
        <h1>Pluviométrie Nationale</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Chargement des données
    df = load_pluviometry()
    gdf = load_geodata()
    
    # Création de la carte
    m = folium.Map(location=[34, 9], zoom_start=6, tiles="cartodbpositron")
    
    folium.Choropleth(
        geo_data=gdf,
        data=df,
        columns=["gouvernorat", "pluviometrie"],
        key_on="feature.properties.name",
        fill_color="YlGnBu",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Pluviométrie (mm)",
        highlight=True
    ).add_to(m)
    
    # Affichage
    with st.container():
        st.markdown('<div class="folium-container">', unsafe_allow_html=True)
        st_folium(m, width=1200, height=600)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Tableau de données
    if show_table:
        st.dataframe(df, use_container_width=True)

def regional_page():
    """Page pluviométrie régionale"""
    with st.sidebar:
        st.write("**Filtres Régionaux**")
        region = st.radio("Région", ["Siliana", "Kairouan"], label_visibility="collapsed")
        year = st.slider("Année", 2015, 2023, 2022)
        resolution = st.selectbox("Résolution", ["Mensuelle", "Trimestrielle", "Annuelle"])
    
    st.markdown("""
    <div class="section-header">
        <h1>Pluviométrie Régionale</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Implémentez votre logique pour Siliana/Kairouan ici
    st.write(f"Contenu spécifique à la région {region} pour l'année {year}")

def biologique_page():
    """Page répartition biologique"""
    with st.sidebar:
        st.write("**Filtres Biologiques**")
        crop_type = st.selectbox("Type de culture", ["Céréales", "Arboriculture", "Légumes", "Toutes"], label_visibility="collapsed")
        year = st.slider("Année", 2010, 2023, 2022)
        show_organic = st.checkbox("Afficher seulement bio", False)
    
    st.markdown(f"""
    <div class="section-header" style="background:linear-gradient(to right, {COLORS['primary']}, #F27D16);">
        <h1>Répartition Biologique</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Implémentez votre logique biologique ici
    st.write(f"Contenu sur la répartition biologique pour {crop_type}")

def eau_page():
    """Page eau potable"""
    with st.sidebar:
        st.write("**Filtres Eau Potable**")
        year = st.slider("Année", 2010, 2023, 2022, label_visibility="collapsed")
        indicator = st.selectbox("Indicateur", ["Accès", "Qualité", "Quantité"])
        show_trend = st.checkbox("Afficher tendance", True)
    
    st.markdown(f"""
    <div class="section-header" style="background:linear-gradient(to right, {COLORS['primary']}, #00A0C8);">
        <h1>Ressources en Eau Potable</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Implémentez votre logique eau potable ici
    st.write(f"Contenu sur les ressources en eau potable - {indicator}")

# =============================================
# ROUTER PRINCIPAL
# =============================================

def get_current_page():
    """Détection de la page active (méthode moderne)"""
    if hasattr(st, 'query_params'):
        return st.query_params.get("page", ["Accueil"])[0]
    return "Accueil"

# Application principale
current_page = get_current_page()
render_navbar(current_page)

if current_page == "Pluviometrie":
    pluviometrie_page()
elif current_page == "rainfall_map":
    regional_page()
elif current_page == "Repartition_Biol":
    biologique_page()
elif current_page == "Eau_Portale":
    eau_page()
else:
    home_page()

st.markdown("</div>", unsafe_allow_html=True)  # Fermeture du main-content