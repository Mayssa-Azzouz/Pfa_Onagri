import streamlit as st
import pandas as pd
import json
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- Configuration de la page ---
st.set_page_config(
    layout="wide",
    page_title="SmartSDGTunisia - Données Pluviométriques",
    page_icon="🌧️",
    initial_sidebar_state="collapsed"
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
        background-color: {COLORS['dark_blue']} !important;
        padding: 0;
    }}
    
    .stSidebar .css-1oe5cao {{
        color: white !important;
    }}
    
    .stApp {{
        background-color: {COLORS['light_gray']};
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }}
    
    h1, h2, h3, h4 {{
        color: {COLORS['dark_blue']};
        font-weight: 600;
    }}
    
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
    
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['dark_blue']} !important;
    }}
    
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, {COLORS['dark_blue']}, #1E1E3C) !important;
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
    
    .folium-map {{
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        border: 1px solid {COLORS['light_gray']} !important;
    }}
    
    .stSuccess, .stInfo, .stWarning, .stError {{
        border-radius: 8px !important;
        padding: 12px 16px !important;
    }}

    /* Style pour les KPI locaux */
    .local-kpi-container {{
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid rgba(0,0,0,0.05);
    }}
    
    .local-kpi-title {{
        color: {COLORS['dark_blue']};
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
        background: {COLORS['vivid_orange']};
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
        color: {COLORS['dark_blue']};
        text-align: center;
        padding: 5px;
        border-radius: 12px;
        background: rgba(0,180,216,0.1);
    }}
</style>
""", unsafe_allow_html=True)

# --- Chargement des données ---
@st.cache_data
def load_data():
    # Charger les données Excel
    df = pd.read_excel("Rainfall_data.xlsx", sheet_name="Data")
    
    # Charger les informations des stations
    stations_df = pd.read_excel("Rainfall_data.xlsx", sheet_name="Note")
    stations_df = stations_df.rename(columns={"N": "ID", "Name": "Station"})
    
    # Calculer les moyennes par station
    numeric_cols = [col for col in df.columns if col != "Date"]
    df_mean = df[numeric_cols].mean().reset_index()
    df_mean.columns = ['ID', 'Valeur']
    df_mean['ID'] = df_mean['ID'].astype(int)
    
    # Fusionner avec les informations des stations
    merged_df = pd.merge(df_mean, stations_df, on="ID")
    
    return df, merged_df

df, merged_df = load_data()

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['soft_purple']}, {COLORS['sky_blue']});
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    ">
        <h2 style="color: white; margin: 0; font-weight: 700;">Données Pluviométriques</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
            Analyse des précipitations en Tunisie (1982-2018)
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Options de filtrage
    st.markdown("### 🔍 Filtres")
    selected_year = st.slider("Année", 1982, 2018, (2000, 2010))
    show_map = st.checkbox("Afficher la carte", value=True)
    show_stats = st.checkbox("Afficher les statistiques", value=True)

# --- En-tête Principal ---
st.markdown(f"""
<div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
    <h1 style="color: {COLORS['dark_blue']}; margin: 0; text-align: center; font-weight: 700;">
        🌧️ SmartSDGTunisia - Données Pluviométriques
    </h1>
    <p style="color: {COLORS['dark_blue']}90; text-align: center; margin: 10px 0 0 0; font-size: 16px;">
        Visualisation des données de précipitations par station météorologique
    </p>
</div>
""", unsafe_allow_html=True)

# --- Section KPI Nationaux ---
st.markdown(f"""
<div style="background:{COLORS['dark_blue']}; padding:15px; border-radius:10px; margin-bottom:25px">
    <h2 style="color:white; text-align:center; margin:0">📊 INDICATEURS PLUVIOMÉTRIQUES</h2>
</div>
""", unsafe_allow_html=True)

# Calcul des KPI
avg_rainfall = merged_df['Valeur'].mean()
max_rainfall = merged_df['Valeur'].max()
min_rainfall = merged_df['Valeur'].min()
station_count = len(merged_df)

# Ligne 1 - KPI Principaux
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['sky_blue']}; text-align:center">
        <h3>🌧️ Précipitation moyenne</h3>
        <h1 style="color:{COLORS['sky_blue']}">{avg_rainfall:.1f} mm</h1>
        <p>Sur toutes les stations</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['mint_green']}; text-align:center">
        <h3>⬆️ Maximum</h3>
        <h1 style="color:{COLORS['mint_green']}">{max_rainfall:.1f} mm</h1>
        <p>Station: {merged_df.loc[merged_df['Valeur'].idxmax(), 'Station']}</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['vivid_orange']}; text-align:center">
        <h3>⬇️ Minimum</h3>
        <h1 style="color:{COLORS['vivid_orange']}">{min_rainfall:.1f} mm</h1>
        <p>Station: {merged_df.loc[merged_df['Valeur'].idxmin(), 'Station']}</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['raspberry_pink']}; text-align:center">
        <h3>📍 Stations</h3>
        <h1 style="color:{COLORS['raspberry_pink']}">{station_count}</h1>
        <p>Stations météorologiques</p>
    </div>
    """, unsafe_allow_html=True)

# --- Carte et Statistiques ---
if show_map or show_stats:
    col_map, col_stats = st.columns([2, 1], gap="medium")
    
    with col_map:
        if show_map:
            st.markdown(f"<h2 class='section-title'>🗺️ Carte des Stations</h2>", unsafe_allow_html=True)
            
            # Création de la carte Folium
            m = folium.Map(location=[merged_df['Lat'].mean(), merged_df['Long'].mean()], zoom_start=7)
            
            # Ajouter les stations
            for idx, row in merged_df.iterrows():
                folium.CircleMarker(
                    location=[row['Lat'], row['Long']],
                    radius=row['Valeur']/10,
                    popup=f"{row['Station']}<br>Moyenne: {row['Valeur']:.1f} mm",
                    color=COLORS['sky_blue'],
                    fill=True,
                    fill_color=COLORS['sky_blue']
                ).add_to(m)
            
            # Afficher la carte
            st_folium(m, width="100%", height=500)
    
    with col_stats:
        if show_stats:
            st.markdown("""
            <div class="local-kpi-container">
                <div class="local-kpi-title">📊 STATISTIQUES PAR STATION</div>
            """, unsafe_allow_html=True)
            
            # Sélection de la station
            selected_station = st.selectbox(
                "Choisir une station",
                options=merged_df['Station'].unique(),
                index=0
            )
            
            # Afficher les KPI pour la station sélectionnée
            station_data = merged_df[merged_df['Station'] == selected_station].iloc[0]
            
            col_kpi1, col_kpi2 = st.columns(2)
            
            with col_kpi1:
                st.markdown(f"""
                <div class="local-kpi-card">
                    <div class="local-kpi-label">Précipitation moyenne</div>
                    <div class="local-kpi-value" style="color:{COLORS['sky_blue']}">{station_data['Valeur']:.1f} mm</div>
                    <div class="local-kpi-comparison">
                        {(station_data['Valeur']/avg_rainfall*100):.1f}% de la moyenne nationale
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_kpi2:
                st.markdown(f"""
                <div class="local-kpi-card">
                    <div class="local-kpi-label">Coordonnées</div>
                    <div class="local-kpi-value" style="color:{COLORS['mint_green']}; font-size:1.2rem;">
                        {station_data['Lat']:.2f}°N, {station_data['Long']:.2f}°E
                    </div>
                    <div class="local-kpi-comparison">
                        ID: {station_data['ID']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Classement national
            rank = int(merged_df['Valeur'].rank(ascending=False, method='min').loc[merged_df['Station'] == selected_station].values[0])
            
            st.markdown(f"""
            <div class="local-kpi-card" style="text-align:center; background: rgba(26,26,46,0.03);">
                <div style="font-size:0.9rem; color:#555;">Classement National</div>
                <div style="display:inline-block; margin:0 15px;">
                    <div style="font-size:0.8rem;">Précipitations</div>
                    <div style="font-size:1.5rem; font-weight:700; color:{COLORS['dark_blue']}">#{rank}</div>
                </div>
            </div>
            </div>  <!-- Fermeture du container -->
            """, unsafe_allow_html=True)
            
            # Données détaillées
            st.markdown(f"<h2 class='section-title'>📋 Données Complètes</h2>", unsafe_allow_html=True)
            st.dataframe(station_data.to_frame().T, 
                        hide_index=True,
                        use_container_width=True)

# --- Visualisation des données temporelles ---
st.markdown(f"<h2 class='section-title'>📈 Évolution Temporelle</h2>", unsafe_allow_html=True)

# Sélection des stations à visualiser
selected_stations = st.multiselect(
    "Sélectionnez les stations à visualiser",
    options=merged_df['Station'].unique(),
    default=merged_df.nlargest(3, 'Valeur')['Station'].tolist()
)

if selected_stations:
    # Filtrer les données pour les stations sélectionnées
    station_ids = merged_df[merged_df['Station'].isin(selected_stations)]['ID'].tolist()
    df_filtered = df[['Date'] + [str(id) for id in station_ids]]
    df_filtered = df_filtered.melt(id_vars='Date', var_name='ID', value_name='Précipitation')
    df_filtered['ID'] = df_filtered['ID'].astype(int)
    df_filtered = pd.merge(df_filtered, merged_df[['ID', 'Station']], on='ID')
    
    # Créer le graphique
    fig = px.line(
        df_filtered, 
        x='Date', 
        y='Précipitation', 
        color='Station',
        title='Évolution des précipitations par station',
        labels={'Précipitation': 'Précipitation (mm)', 'Date': 'Date'},
        color_discrete_sequence=[COLORS['sky_blue'], COLORS['mint_green'], COLORS['vivid_orange'], 
                               COLORS['raspberry_pink'], COLORS['soft_purple']]
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Veuillez sélectionner au moins une station pour visualiser les données temporelles.")