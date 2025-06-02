import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point
from scripts.geo_utils import load_geodata
from scripts.data_utils import load_pluviometry

# --- Configuration de la page ---
st.set_page_config(
    layout="wide",
    page_title="ONAGRI - Répartition biologique",
    page_icon="🌱",
    initial_sidebar_state="auto"
)

# 🎨 Palette de couleurs cohérente avec le thème vert
COLORS = {
    "primary": "#1E6C41",      # Vert foncé
    "secondary": "#2E7D32",    # Vert
    "accent": "#4CAF50",       # Vert clair
    "background": "#F5FBF5",   # Fond très clair
    "text": "#263238",         # Texte foncé
    "white": "#FFFFFF",
    "light_gray": "#F0F0F0",
    "orange": "#F27D16"        # Orange pour les accents
}

# --- CSS Personnalisé ---
st.markdown(f"""
<style>
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
    
    /* Ajustement de la position du contenu */
    .block-container {{
        padding-top: 80px;
    }}

    /* Style global existant */
    [data-testid="stHeader"] {{
        background-color: {COLORS['primary']} !important;
        padding: 0;
    }}
    
    .stSidebar .css-1oe5cao {{
        color: white !important;
    }}
    
    .stApp {{
        background-color: {COLORS['background']};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    h1, h2, h3, h4 {{
        color: {COLORS['primary']};
        font-weight: 600;
    }}
    
    .card {{
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border-left: 4px solid {COLORS['accent']};
        transition: all 0.3s ease;
    }}
    
    .card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }}
    
    .section-title {{
        color: {COLORS['primary']};
        border-bottom: 2px solid {COLORS['orange']};
        padding-bottom: 8px;
        margin-bottom: 20px;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['primary']} !important;
    }}
    
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, {COLORS['primary']}, #1E3C1E) !important;
        padding: 20px 15px !important;
    }}
    
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
    
    .stButton>button {{
        background: {COLORS['orange']} !important;
        color: white !important;
        border-radius: 8px !important;
        padding: 10px 16px !important;
        font-weight: 500 !important;
        transition: all 0.3s ease !important;
        border: none !important;
    }}
    
    .stButton>button:hover {{
        background: {COLORS['secondary']} !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1) !important;
    }}
    
    .folium-map {{
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        border: 1px solid {COLORS['light_gray']} !important;
    }}
    
    .stSuccess, .stInfo, .stWarning, .stError {{
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }}

    /* Nouveau style pour les KPI locaux */
    .local-kpi-container {{
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid rgba(0,0,0,0.05);
    }}
    
    .local-kpi-title {{
        color: {COLORS['primary']};
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 20px;
        text-align: center;
        position: relative;
    }}
    
    .local-kpi-title:after {{
        content: "";
        display: block;
        width: 50px;
        height: 3px;
        background: {COLORS['orange']};
        margin: 8px auto 0;
    }}
    
    .local-kpi-card {{
        background: white;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        border: none;
    }}
    
    .local-kpi-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}
    
    .local-kpi-value {{
        font-size: 2rem;
        font-weight: 700;
        margin: 10px 0;
        text-align: center;
    }}
    
    .local-kpi-label {{
        font-size: 0.9rem;
        color: #666;
        text-align: center;
        margin-bottom: 5px;
    }}
    
    .local-kpi-comparison {{
        font-size: 0.8rem;
        color: {COLORS['primary']};
        text-align: center;
        padding: 5px;
        border-radius: 12px;
        background: rgba(30,108,65,0.1);
    }}
    
    /* Barre de navigation modernisée */
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
    
    .main-content {{
        padding-top: 5rem;
        padding-bottom: 2rem;
    }}
</style>
""", unsafe_allow_html=True)

# --- Fonction pour afficher la navbar ---
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
                <a href="/Climat" class="nav-link {'active' if current == 'Climat' else ''}" target="_self">
                    <span class="nav-icon">🌤️</span> Climat
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

# --- Afficher la navbar avec l'onglet actif ---
render_navbar("Répartition Bio")

# --- Chargement des données ---
gdf_gouv, gdf_del = load_geodata()

@st.cache_data
def load_bio_data(file_path):
    df_bio = pd.read_excel(file_path)
    return df_bio

df_bio = load_bio_data("data/repartition_bio.xlsx")

# --- Calcul des KPI globaux ---
total_oliviers = df_bio['OLIVIER'].sum()
total_palmiers = df_bio['PALMIER_DATTIER'].sum()
gouvernorats_actifs = len(df_bio[df_bio['OLIVIER'] > 0])
surface_forestiere = df_bio['foret'].sum()
surface_arboriculture = df_bio['arboriculture'].sum()
surface_agricole = df_bio[['arboriculture', 'maraichage', 'grandes_cultures']].sum().sum()

# Top 3 des gouvernorats
top_oliviers = df_bio.nlargest(3, 'OLIVIER')[['GOUVERNORAT', 'OLIVIER']]
top_palmiers = df_bio.nlargest(3, 'PALMIER_DATTIER')[['GOUVERNORAT', 'PALMIER_DATTIER']]

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['orange']});
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    ">
        <h2 style="color: white; margin: 0; font-weight: 700;">Répartition Biologique</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
            Analyse interactive de répartition biologique
        </p>
    </div>
    """, unsafe_allow_html=True)

# --- En-tête Principal ---
st.markdown(f"""
<div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
    <h1 style="color: {COLORS['primary']}; margin: 0; text-align: center; font-weight: 700;">
        🌱 Répartition Biologique en Tunisie
    </h1>
    <p style="color: {COLORS['primary']}90; text-align: center; margin: 10px 0 0 0; font-size: 16px;">
        Plateforme de visualisation des cultures et de la biodiversité agricole
    </p>
</div>
""", unsafe_allow_html=True)

# --- Section KPI Nationaux ---
st.markdown(f"""
<div style="background:{COLORS['primary']}; padding:15px; border-radius:10px; margin-bottom:25px">
    <h2 style="color:white; text-align:center; margin:0">📊 INDICATEURS NATIONAUX</h2>
</div>
""", unsafe_allow_html=True)

# Ligne 1 - KPI Principaux
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['accent']}; text-align:center">
        <h3>🌳 Oliviers</h3>
        <h1 style="color:{COLORS['accent']}">{total_oliviers:,}</h1>
        <p>+12% vs 2022</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['secondary']}; text-align:center">
        <h3>🌴 Palmiers</h3>
        <h1 style="color:{COLORS['secondary']}">{total_palmiers:,}</h1>
        <p>Dont 80% à Tozeur</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['orange']}; text-align:center">
        <h3>🏞️ Surfaces</h3>
        <h1 style="color:{COLORS['orange']}">{surface_agricole:,} ha</h1>
        <p>Dont {surface_forestiere:,} ha forestiers</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['primary']}; text-align:center">
        <h3>📍 Couverture</h3>
        <h1 style="color:{COLORS['primary']}">{gouvernorats_actifs}/24</h1>
        <p>Gouvernorats productifs</p>
    </div>
    """, unsafe_allow_html=True)

# Ligne 2 - Top 3
st.markdown("<br>", unsafe_allow_html=True)
col5, col6 = st.columns(2)

with col5:
    st.markdown(f"""
    <div class="card">
        <h3 style="color:{COLORS['primary']}">🏆 Top 3 Oliviers</h3>
        <table style="width:100%">
            <tr><th>Gouvernorat</th><th>Nombre</th><th>Part</th></tr>
            <tr><td>{top_oliviers.iloc[0,0]}</td><td>{top_oliviers.iloc[0,1]:,}</td><td>{(top_oliviers.iloc[0,1]/total_oliviers*100):.1f}%</td></tr>
            <tr><td>{top_oliviers.iloc[1,0]}</td><td>{top_oliviers.iloc[1,1]:,}</td><td>{(top_oliviers.iloc[1,1]/total_oliviers*100):.1f}%</td></tr>
            <tr><td>{top_oliviers.iloc[2,0]}</td><td>{top_oliviers.iloc[2,1]:,}</td><td>{(top_oliviers.iloc[2,1]/total_oliviers*100):.1f}%</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

with col6:
    st.markdown(f"""
    <div class="card">
        <h3 style="color:{COLORS['primary']}">🏆 Top 3 Palmiers</h3>
        <table style="width:100%">
            <tr><th>Gouvernorat</th><th>Nombre</th><th>Part</th></tr>
            <tr><td>{top_palmiers.iloc[0,0]}</td><td>{top_palmiers.iloc[0,1]:,}</td><td>{(top_palmiers.iloc[0,1]/total_palmiers*100):.1f}%</td></tr>
            <tr><td>{top_palmiers.iloc[1,0]}</td><td>{top_palmiers.iloc[1,1]:,}</td><td>{(top_palmiers.iloc[1,1]/total_palmiers*100):.1f}%</td></tr>
            <tr><td>{top_palmiers.iloc[2,0]}</td><td>{top_palmiers.iloc[2,1]:,}</td><td>{(top_palmiers.iloc[2,1]/total_palmiers*100):.1f}%</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

# Séparateur
st.markdown("---")

# --- Carte et KPI Locaux ---
col_map, col_kpi = st.columns([2, 1], gap="medium")

with col_map:
    st.markdown(f"<h2 class='section-title'>🗺️ Carte Interactive</h2>", unsafe_allow_html=True)
    
    # Création de la carte
    m = folium.Map(location=[34, 9], zoom_start=6, tiles="cartodbpositron")
    style_gouv = {
        'fillColor': COLORS['accent'],
        'color': COLORS['primary'],
        'weight': 2,
        'fillOpacity': 0.3
    }
    folium.GeoJson(gdf_gouv, name="Gouvernorats", 
                  style_function=lambda x: style_gouv,
                  tooltip=folium.GeoJsonTooltip(fields=['gouv_fr'], aliases=["Gouvernorat:"])).add_to(m)
    folium.LayerControl().add_to(m)
    
    # Affichage de la carte
    map_data = st_folium(
        m, 
        height=700, 
        width="100%", 
        returned_objects=["last_object_clicked", "last_active_drawing"]
    )
    
    # Gestion du clic sur la carte
    if map_data and (map_data.get("last_object_clicked") or map_data.get("last_active_drawing")):
        clicked_data = map_data.get("last_active_drawing") or map_data.get("last_object_clicked")
        try:
            clicked_gouv = clicked_data["properties"]["gouv_fr"]
            st.session_state.selected_gouv = clicked_gouv
            st.success(f"Gouvernorat sélectionné: {clicked_gouv}")
        except (KeyError, TypeError):
            st.warning("Veuillez cliquer sur un gouvernorat")

with col_kpi:
    st.markdown("""
    <div class="local-kpi-container">
        <div class="local-kpi-title">📊 PERFORMANCE LOCALE</div>
    """, unsafe_allow_html=True)
    
    # Liste des gouvernorats pour la sélection manuelle
    gouvernorats = sorted(df_bio['GOUVERNORAT'].unique().tolist())
    
    # Sélection du gouvernorat (carte ou menu)
    if "selected_gouv" not in st.session_state:
        st.session_state.selected_gouv = gouvernorats[0]
    
    selected_gouv = st.selectbox(
        "Choisir un gouvernorat",
        options=gouvernorats,
        index=gouvernorats.index(st.session_state.selected_gouv) if st.session_state.selected_gouv in gouvernorats else 0
    )
    st.session_state.selected_gouv = selected_gouv
    
    # Affichage des KPI locaux
    if st.session_state.selected_gouv in df_bio['GOUVERNORAT'].values:
        gouv_data = df_bio[df_bio['GOUVERNORAT'] == st.session_state.selected_gouv].iloc[0]
        
        # Layout des KPI
        col_kpi1, col_kpi2 = st.columns(2)
        
        with col_kpi1:
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Oliviers</div>
                <div class="local-kpi-value" style="color:{COLORS['accent']}">{gouv_data['OLIVIER']:,}</div>
                <div class="local-kpi-comparison">
                    {(gouv_data['OLIVIER']/total_oliviers*100):.1f}% du national
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Surface Arboricole</div>
                <div class="local-kpi-value" style="color:{COLORS['primary']}">{gouv_data['arboriculture']:,} ha</div>
                <div class="local-kpi-comparison">
                    {(gouv_data['arboriculture']/surface_arboriculture*100):.1f}% du national
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_kpi2:
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Palmiers Dattiers</div>
                <div class="local-kpi-value" style="color:{COLORS['secondary']}">{gouv_data['PALMIER_DATTIER']:,}</div>
                <div class="local-kpi-comparison">
                    {(gouv_data['PALMIER_DATTIER']/total_palmiers*100):.1f}% du national
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Surface Forestière</div>
                <div class="local-kpi-value" style="color:{COLORS['orange']}">{gouv_data['foret']:,} ha</div>
                <div class="local-kpi-comparison">
                    {(gouv_data['foret']/surface_forestiere*100):.1f}% du national
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Classement national
        rank_olivier = int(df_bio['OLIVIER'].rank(ascending=False, method='min').loc[df_bio['GOUVERNORAT'] == st.session_state.selected_gouv].values[0])
        
        st.markdown(f"""
        <div class="local-kpi-card" style="text-align:center; background: rgba(30,108,65,0.03);">
            <div style="font-size:0.9rem; color:#555;">Classement National</div>
            <div style="display:inline-block; margin:0 15px;">
                <div style="font-size:0.8rem;">Oliviers</div>
                <div style="font-size:1.5rem; font-weight:700; color:{COLORS['primary']}">#{rank_olivier}</div>
            </div>
        </div>
        </div>  <!-- Fermeture du container -->
        """, unsafe_allow_html=True)
        
        # Données détaillées
        st.markdown(f"<h2 class='section-title'>📋 Données Complètes</h2>", unsafe_allow_html=True)
        st.dataframe(gouv_data.to_frame().T, 
                    hide_index=True,
                    use_container_width=True,
                    column_config={
                        "GOUVERNORAT": "Gouvernorat",
                        "OLIVIER": st.column_config.NumberColumn("Oliviers", format="%d"),
                        "PALMIER_DATTIER": st.column_config.NumberColumn("Palmiers", format="%d"),
                        "foret": st.column_config.NumberColumn("Forêt (ha)", format="%d")
                    })
    else:
        st.markdown("""
        <div style="text-align:center; padding:30px; color:#666;">
            Sélectionnez un gouvernorat pour voir les statistiques locales
        </div>
        </div>  <!-- Fermeture du container -->
        """, unsafe_allow_html=True)

# Fermeture du main-content
st.markdown("</div>", unsafe_allow_html=True)