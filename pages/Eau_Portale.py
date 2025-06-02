import streamlit as st
import folium
import pandas as pd
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point
from scripts.geo_utils import load_geodata

# --- Configuration de la page ---
st.set_page_config(
    layout="wide",
    page_title="SmartSDGTunisia - Eau Potable",
    page_icon="💧",
    initial_sidebar_state="expanded"
)

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
    
    /* Navigation modernisée */
    .navbar {{
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_end']});
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
    
    /* Application principale */
    .stApp {{
        background-color: {COLORS['bg_green']};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: {COLORS['dark_text']};
        line-height: 1.6;
    }}
    
    /* Ajustement de la position du contenu */
    .main-content {{
        padding-top: 5rem;
        padding-bottom: 2rem;
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
    
    /* Style ajouté pour le graphique d'évolution */
    .evolution-container {{
        margin-top: 30px;
        background: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }}
    
    /* Responsive */
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
    }}
</style>
""", unsafe_allow_html=True)

# --- Barre de navigation ---
def render_navbar(current_page="Eau Potable"):
    st.markdown(f"""
    <nav class="navbar">
        <div class="nav-container">
            <div class="nav-brand">🌱 SmartSDGTunisia</div>
            <div class="nav-links">
                <a href="/" class="nav-link {'active' if current_page == 'Accueil' else ''}" target="_self">
                    <span class="nav-icon">🏠</span> Accueil
                </a>
                <a href="/Eau_Portale" class="nav-link {'active' if current_page == 'Eau Potable' else ''}" target="_self">
                    <span class="nav-icon">💧</span> Eau Potable
                </a>
                <a href="/Pluviometrie" class="nav-link {'active' if current_page == 'Pluviométrie' else ''}" target="_self">
                    <span class="nav-icon">🌧️</span> Pluviométrie
                </a>
                <a href="/rainfall_map" class="nav-link {'active' if current_page == 'Pluviométrie Région' else ''}" target="_self">
                    <span class="nav-icon">🌦️</span> Siliana/Kairouan
                </a>
                <a href="/Repartition_Biol" class="nav-link {'active' if current_page == 'Répartition Bio' else ''}" target="_self">
                    <span class="nav-icon">🧬</span> Biologique
                </a>
            </div>
        </div>
    </nav>
    <div class="main-content">
    """, unsafe_allow_html=True)

# --- Affichage de la navbar ---
render_navbar("Eau portable")


# --- Chargement des données ---
@st.cache_data
def load_water_data():
    df = pd.read_csv("data/eau_portale.csv")
    # Nettoyage des données
    df['gouvernorat'] = df['gouvernorat'].str.strip()
    # Exclure la ligne du coefficient de pointe
    df = df[~df['gouvernorat'].str.contains("Coefficient de pointe", na=False)]
    return df

df_water = load_water_data()
gdf_gouv, _ = load_geodata()

# Fusion avec les données géographiques
gdf_water = gdf_gouv.merge(df_water, left_on='gouv_fr', right_on='gouvernorat')

# Calcul des indicateurs globaux
total_annual = df_water[['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                        'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']].sum().sum()
avg_monthly = df_water[['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                       'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']].mean().mean()
max_month = df_water[['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                     'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']].sum().idxmax()
max_value = df_water[['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                     'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']].sum().max()

# Top 3 des gouvernorats (moyenne annuelle)
df_water['Moyenne_annuelle'] = df_water[['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                                        'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']].mean(axis=1)
top_gouvernorats = df_water.nlargest(3, 'Moyenne_annuelle')[['gouvernorat', 'Moyenne_annuelle']]

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_end']});
        padding: 25px 20px;
        border-radius: 16px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    ">
        <div class="sidebar-title">💧 Eau Potable</div>
        <div class="sidebar-subtitle">Consommation mensuelle par gouvernorat</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sélection du mois
    selected_month = st.selectbox(
        "Sélectionnez un mois",
        options=['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre'],
        index=6  # Juillet par défaut (pic de consommation)
    )

# --- En-tête Principal ---
st.markdown(f"""
<div style="background: white; padding: 15px; border-radius: 16px; margin-bottom: 15px; box-shadow: 0 8px 20px rgba(0,0,0,0.1);">
    <h1 style="color: {COLORS['primary_green']}; margin: 0; text-align: center; font-weight: 700;">
        💧 SmartSDGTunisia - Consommation d'Eau Potable
    </h1>
    <p style="color: {COLORS['light_text']}; text-align: center; margin: 10px 0 0 0; font-size: 16px;">
        Analyse de la consommation mensuelle par gouvernorat
    </p>
</div>
""", unsafe_allow_html=True)

# --- Section KPI Nationaux ---
st.markdown(f"""
<div style="background:{COLORS['primary_green']}; padding:5px; border-radius:5px; margin-bottom:10px">
    <h2 style="color:white; text-align:center; margin:0">📊 INDICATEURS NATIONAUX</h2>
</div>
""", unsafe_allow_html=True)

# Ligne 1 - KPI Principaux
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['primary_green']}; text-align:center">
        <h3>💧 Consommation annuelle</h3>
        <h1 style="color:{COLORS['primary_green']}">{total_annual:,.0f}</h1>
        <p>m³ (milliers)</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['light_green']}; text-align:center">
        <h3>📅 Moyenne mensuelle</h3>
        <h1 style="color:{COLORS['light_green']}">{avg_monthly:,.0f}</h1>
        <p>m³ (milliers)</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['dark_green']}; text-align:center">
        <h3>🔥 Mois de pic</h3>
        <h1 style="color:{COLORS['dark_green']}">{max_month}</h1>
        <p>{max_value:,.0f} m³ (milliers)</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['accent_blue']}; text-align:center">
        <h3>🌡️ Variation saisonnière</h3>
        <h1 style="color:{COLORS['accent_blue']}">+{(max_value/avg_monthly-1)*100:.0f}%</h1>
        <p>Pic vs moyenne</p>
    </div>
    """, unsafe_allow_html=True)

# Ligne 2 - Top 3
st.markdown("<br>", unsafe_allow_html=True)
col5, col6 = st.columns(2)

with col5:
    st.markdown(f"""
    <div class="card">
        <h3 style="color:{COLORS['primary_green']}">🏆 Top 3 Consommation</h3>
        <table style="width:100%">
            <tr><th>Gouvernorat</th><th>Moyenne (m³)</th><th>Part</th></tr>
            <tr><td>{top_gouvernorats.iloc[0,0]}</td><td>{top_gouvernorats.iloc[0,1]:,.0f}</td><td>{(top_gouvernorats.iloc[0,1]/avg_monthly/24*100):.1f}%</td></tr>
            <tr><td>{top_gouvernorats.iloc[1,0]}</td><td>{top_gouvernorats.iloc[1,1]:,.0f}</td><td>{(top_gouvernorats.iloc[1,1]/avg_monthly/24*100):.1f}%</td></tr>
            <tr><td>{top_gouvernorats.iloc[2,0]}</td><td>{top_gouvernorats.iloc[2,1]:,.0f}</td><td>{(top_gouvernorats.iloc[2,1]/avg_monthly/24*100):.1f}%</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

with col6:
    # Évolution mensuelle nationale
    monthly_totals = df_water[['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                             'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']].sum()
    
    # Convertir les données en DataFrame pour st.line_chart
    chart_data = pd.DataFrame({
        'Mois': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
        'Consommation': monthly_totals.values
    }).set_index('Mois')
    
    st.markdown(f"""
    <div class="card">
        <h3 style="color:{COLORS['primary_green']}">📈 Évolution mensuelle nationale</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.line_chart(chart_data, color=COLORS['primary_green'], height=200)

# Séparateur
st.markdown("---")

# --- Carte et KPI Locaux ---
col_map, col_kpi = st.columns([2, 1], gap="medium")

with col_map:
    st.markdown(f"<h2 class='section-title'>🗺️ Carte de Consommation - {selected_month}</h2>", unsafe_allow_html=True)
    
    # Création de la carte choroplèthe
    m = folium.Map(location=[34, 9], zoom_start=6, tiles="cartodbpositron")
    
    # Choropleth avec les données d'eau
    folium.Choropleth(
        geo_data=gdf_water,
        name="Consommation",
        data=df_water,
        columns=["gouvernorat", selected_month],
        key_on="feature.properties.gouv_fr",
        fill_color="Greens",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f"Consommation d'eau ({selected_month}) en m³",
        highlight=True
    ).add_to(m)
    
    # Ajout des tooltips
    folium.GeoJson(
        gdf_water,
        name="Gouvernorats",
        style_function=lambda x: {'color':'transparent','fillColor':'transparent','weight':0},
        tooltip=folium.GeoJsonTooltip(
            fields=["gouv_fr", selected_month],
            aliases=["Gouvernorat: ", f"{selected_month}: "],
            localize=True,
            sticky=True,
            labels=True,
            style="""
                background-color: #FFFFFF;
                border: 1px solid #000000;
                border-radius: 3px;
                box-shadow: 3px 3px rgba(0,0,0,0.1);
                padding: 3px;
            """
        )
    ).add_to(m)
    
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
    gouvernorats = sorted([str(x) for x in df_water['gouvernorat'].unique().tolist()])
    
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
    if st.session_state.selected_gouv in df_water['gouvernorat'].values:
        gouv_data = df_water[df_water['gouvernorat'] == st.session_state.selected_gouv].iloc[0]
        monthly_data = gouv_data[['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                                'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']]
        
        # Layout des KPI
        col_kpi1, col_kpi2 = st.columns(2)
        
        with col_kpi1:
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Consommation ({selected_month})</div>
                <div class="local-kpi-value" style="color:{COLORS['primary_green']}">{gouv_data[selected_month]:,.0f}</div>
                <div class="local-kpi-comparison">
                    {(gouv_data[selected_month]/df_water[selected_month].sum()*100):.1f}% du national
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Moyenne annuelle</div>
                <div class="local-kpi-value" style="color:{COLORS['dark_green']}">{monthly_data.mean():,.0f}</div>
                <div class="local-kpi-comparison">
                    {(monthly_data.mean()/avg_monthly/24*100):.1f}% du national
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        with col_kpi2:
            max_local_month = monthly_data.idxmax()
            min_local_month = monthly_data.idxmin()
            
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Mois de pic</div>
                <div class="local-kpi-value" style="color:{COLORS['accent_blue']}">{max_local_month}</div>
                <div class="local-kpi-comparison">
                    {monthly_data[max_local_month]:,.0f} m³ (+{(monthly_data[max_local_month]/monthly_data.mean()-1)*100:.0f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Mois le plus bas</div>
                <div class="local-kpi-value" style="color:{COLORS['light_green']}">{min_local_month}</div>
                <div class="local-kpi-comparison">
                    {monthly_data[min_local_month]:,.0f} m³ ({(monthly_data[min_local_month]/monthly_data.mean()-1)*100:.0f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Classement national
        rank_month = int(df_water[selected_month].rank(ascending=False, method='min').loc[df_water['gouvernorat'] == st.session_state.selected_gouv].values[0])
        rank_annual = int(df_water['Moyenne_annuelle'].rank(ascending=False, method='min').loc[df_water['gouvernorat'] == st.session_state.selected_gouv].values[0])
        
        st.markdown(f"""
        <div class="local-kpi-card" style="text-align:center; background: rgba(30,108,65,0.03);">
            <div style="font-size:0.9rem; color:#555;">Classement National</div>
            <div style="display:flex; justify-content:space-around; margin-top:10px;">
                <div>
                    <div style="font-size:0.8rem;">{selected_month}</div>
                    <div style="font-size:1.2rem; font-weight:700; color:{COLORS['primary_green']}">#{rank_month}</div>
                </div>
                <div>
                    <div style="font-size:0.8rem;">Annuel</div>
                    <div style="font-size:1.2rem; font-weight:700; color:{COLORS['primary_green']}">#{rank_annual}</div>
                </div>
            </div>
        </div>
        </div>  <!-- Fermeture du container -->
        """, unsafe_allow_html=True)

# --- Graphique d'évolution locale ---
if "selected_gouv" in st.session_state and st.session_state.selected_gouv in df_water['gouvernorat'].values:
    st.markdown(f"<h2 class='section-title'>📈 Évolution Mensuelle - {st.session_state.selected_gouv}</h2>", unsafe_allow_html=True)
    
    with st.container():
        st.markdown(f"""
        <div class="evolution-container">
            <h3 style="color:{COLORS['primary_green']}; margin-bottom: 20px;">Consommation mensuelle</h3>
        </div>
        """, unsafe_allow_html=True)
        
        gouv_data = df_water[df_water['gouvernorat'] == st.session_state.selected_gouv].iloc[0]
        monthly_data = gouv_data[['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                                'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']]
        
        # Préparer les données pour le graphique
        evolution_data = pd.DataFrame({
            'Mois': ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Jun', 
                    'Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
            'Consommation': monthly_data.values
        }).set_index('Mois')
        
        # Afficher le graphique en pleine largeur
        st.line_chart(
            evolution_data,
            use_container_width=True,
            color=COLORS['primary_green'],
            height=400
        )

# --- Données complètes ---
st.markdown(f"<h2 class='section-title'>📋 Données Complètes</h2>", unsafe_allow_html=True)
st.dataframe(
    df_water,
    use_container_width=True,
    hide_index=True,
    column_config={
        "gouvernorat": "Gouvernorat",
        "Janvier": st.column_config.NumberColumn("Janvier", format="%.1f"),
        "Fevrier": st.column_config.NumberColumn("Février", format="%.1f"),
        "Mars": st.column_config.NumberColumn("Mars", format="%.1f"),
        "Avril": st.column_config.NumberColumn("Avril", format="%.1f"),
        "Mai": st.column_config.NumberColumn("Mai", format="%.1f"),
        "Juin": st.column_config.NumberColumn("Juin", format="%.1f"),
        "Juillet": st.column_config.NumberColumn("Juillet", format="%.1f"),
        "Aout": st.column_config.NumberColumn("Août", format="%.1f"),
        "Septembre": st.column_config.NumberColumn("Septembre", format="%.1f"),
        "Octobre": st.column_config.NumberColumn("Octobre", format="%.1f"),
        "Novembre": st.column_config.NumberColumn("Novembre", format="%.1f"),
        "Decembre": st.column_config.NumberColumn("Décembre", format="%.1f"),
        "Moyenne_annuelle": st.column_config.NumberColumn("Moyenne", format="%.1f")
    }
)

st.markdown("</div>", unsafe_allow_html=True)  # Fermeture du main-content