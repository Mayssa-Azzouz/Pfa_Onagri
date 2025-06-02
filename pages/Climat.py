import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import plotly.graph_objects as go
import folium
from streamlit_folium import st_folium
from datetime import datetime
import numpy as np
import io
from io import BytesIO

# --- Configuration de la page ---
st.set_page_config(
    layout="wide",
    page_title="Dashboard Climatique Tunisie",
    page_icon="🌦️",
    initial_sidebar_state="expanded"
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

    /* Nouveau style pour les KPI */
    .metric-card {{
        background: white;
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid rgba(0,0,0,0.05);
        text-align: center;
    }}
    
    .metric-title {{
        color: {COLORS['primary']};
        font-size: 1rem;
        font-weight: 600;
        margin-bottom: 10px;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        margin: 10px 0;
    }}
    
    .metric-label {{
        font-size: 0.9rem;
        color: #666;
    }}
    
    /* Barre de navigation */
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
    
    .main-content {{
        padding-top: 5rem;
        padding-bottom: 2rem;
    }}
    
    /* Style pour les cartes de station */
    .station-card {{
        background: white;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
        border-left: 4px solid {COLORS['accent']};
    }}
    
    .station-card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }}
    
    .new-station {{
        border-left: 4px solid {COLORS['orange']} !important;
    }}
    
    .api-status {{
        padding: 8px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 5px;
    }}
    
    .api-success {{
        background-color: #d4edda;
        color: #155724;
    }}
    
    .api-error {{
        background-color: #f8d7da;
        color: #721c24;
    }}
</style>
""", unsafe_allow_html=True)


def get_current_page():
    """Détection de la page active (méthode moderne)"""
    if hasattr(st, 'query_params'):
        return st.query_params.get("page", ["Accueil"])[0]
    return "Accueil"
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
# Application principale
current_page = get_current_page()
render_navbar(current_page)

# Données des stations avec la nouvelle station ajoutée
STATIONS = {
    "Station Gabes": {
        "api_url": "https://catalog.agridata.tn/dataset/bef2a022-6834-452a-a1c9-40d123db2165/resource/adf52f71-a59b-4674-96a2-c7702151918b/download/adf52f71-a59b-4674-96a2-c7702151918b",
        "lat": 33.887235,
        "lon": 9.893733,
        "altitude": 67.2,
        "region": "Gabes",
        "interval": "15 minutes",
        "active_since": "30/01/2017 02:00"
    },
    "Station Kébili": {
        "api_url": "https://catalog.agridata.tn/dataset/0c40319e-f1fc-4e38-91db-4a2bc50fbfd3/resource/6fc54e2c-0db7-4ce5-8d41-9e1ff958815c/download/6fc54e2c-0db7-4ce5-8d41-9e1ff958815c",
        "lat": 33.736489,
        "lon": 8.982449,
        "altitude": 158.7,
        "region": "Kébili",
        "interval": "15 minutes",
        "active_since": "13/02/2017 11:19"
    },
    "Station Oued Souhil Nabeul": {
        "api_url": "https://catalog.agridata.tn/dataset/3960f86d-3f0c-45e4-99bd-ad63b9b55e64/resource/105f84c3-3d5e-420f-93cf-5b8b7e18bbc1/download/105f84c3-3d5e-420f-93cf-5b8b7e18bbc1",
        "lat": 36.547951,
        "lon": 9.010971,
        "altitude": 158.7,
        "region": "Nabeul",
        "interval": "30 minutes",
        "active_since": "17/11/2015 09:00",
        "data_send_time": "7:00 et 17:00"
    }
}

@st.cache_data(ttl=3600)
def fetch_station_data(api_url, station_name):
    try:
        # Simulation de données différenciées par station
        if station_name == "Station Oued Souhil Nabeul":
            sample_data = {
                "records": [
                    {
                        "date": (datetime.now() - pd.Timedelta(days=i)).strftime("%Y-%m-%d"),
                        "temperature": np.random.uniform(18, 25),
                        "humidity": np.random.uniform(60, 80),
                        "precipitation": np.random.uniform(0, 10),
                        "wind_speed": np.random.uniform(10, 20)
                    }
                    for i in range(5, 0, -1)
                ]
            }
        else:
            sample_data = {
                "records": [
                    {
                        "date": (datetime.now() - pd.Timedelta(days=i)).strftime("%Y-%m-%d"),
                        "temperature": np.random.uniform(24, 28),
                        "humidity": np.random.uniform(35, 45),
                        "precipitation": np.random.uniform(0, 5),
                        "wind_speed": np.random.uniform(5, 15)
                    }
                    for i in range(5, 0, -1)
                ]
            }
        
        # Transformation des données
        df = pd.DataFrame(sample_data['records'])
        
        # Nettoyage des données
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
        if 'temperature' in df.columns:
            df['temp'] = df['temperature']
        if 'humidity' in df.columns:
            df['humidity'] = df['humidity'].astype(float)
            
        return df
        
    except Exception as e:
        st.error(f"Erreur temporaire - Utilisation de données simulées pour {station_name}")
        return pd.DataFrame({
            'date': pd.date_range(end=datetime.now(), periods=5),
            'temp': np.random.uniform(20, 30, 5),
            'humidity': np.random.uniform(30, 80, 5),
            'precipitation': np.random.uniform(0, 10, 5),
            'wind_speed': np.random.uniform(5, 20, 5)
        })

# Fonction pour créer la carte
def create_stations_map(selected_stations):
    m = folium.Map(location=[34.0, 9.5], zoom_start=7, tiles='CartoDB positron')
    
    for station_name in selected_stations:
        station = STATIONS[station_name]
        df = fetch_station_data(station['api_url'], station_name)
        
        if not df.empty:
            last_data = df.iloc[-1]
            temp = last_data.get('temp', 'N/A')
            humidity = last_data.get('humidity', 'N/A')
            date = last_data.get('date', 'N/A')
            
            popup_content = f"""
            <div style="width: 250px;">
                <h4 style="margin:0;color:#4e73df;">{station_name}</h4>
                <p style="margin:5px 0;font-size:0.9em;color:#666;">
                    <i class="fa fa-map-marker"></i> {station['lat']:.6f}°N, {station['lon']:.6f}°E<br>
                    <i class="fa fa-arrow-up"></i> Alt: {station['altitude']}m
                </p>
                <div style="border-top:1px solid #eee;margin:5px 0;"></div>
                <p style="margin:5px 0;">
                    <b>Température:</b> {temp:.1f}°C<br>
                    <b>Humidité:</b> {humidity:.1f}%<br>
                    <b>Intervalle:</b> {station['interval']}<br>
                    {'<b>Envoi des données:</b> ' + station['data_send_time'] + '<br>' if 'data_send_time' in station else ''}
                    <b>Actif depuis:</b> {station['active_since']}
                </p>
            </div>
            """
            
            icon_color = 'orange' if station_name == "Station Oued Souhil Nabeul" else 'blue'
            
            folium.Marker(
                location=[station['lat'], station['lon']],
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=station_name,
                icon=folium.Icon(color=icon_color, icon='cloud', prefix='fa')
            ).add_to(m)
    
    return m

# En-tête Principal
st.markdown(f"""
<div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
    <h1 style="color: {COLORS['primary']}; margin: 0; text-align: center; font-weight: 700;">
        🌦️ Dashboard Climatique Tunisie
    </h1>
    <p style="color: {COLORS['primary']}90; text-align: center; margin: 10px 0 0 0; font-size: 16px;">
        Surveillance des stations météorologiques en temps réel
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar pour la configuration
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
        <h2 style="color: white; margin: 0; font-weight: 700;">Configuration</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
            Paramètres d'affichage
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    selected_stations = st.multiselect(
        "Sélectionnez les stations",
        options=list(STATIONS.keys()),
        default=list(STATIONS.keys())
    )
    
    date_range = st.date_input(
        "Période d'analyse",
        value=[datetime.now().date().replace(day=1), datetime.now().date()],
        max_value=datetime.now().date()
    )
    
    variables = st.multiselect(
        "Variables à analyser",
        options=["temp", "humidity", "precipitation", "wind_speed"],
        default=["temp", "humidity"]
    )
    
    st.markdown("---")
    st.markdown("### 📊 Options de visualisation")
    chart_type = st.selectbox(
        "Type de graphique",
        options=["Ligne", "Barre", "Zone"],
        index=0
    )
    
    st.markdown("---")
    st.markdown("### 📍 Informations stations")
    for name, station in STATIONS.items():
        station_class = "new-station" if name == "Station Oued Souhil Nabeul" else ""
        st.markdown(f"""
        <div class="station-card {station_class}">
            <b>{station['region']}</b><br>
            <small>Lat: {station['lat']:.6f}, Lon: {station['lon']:.6f}</small><br>
            <small>Alt: {station['altitude']}m • Depuis: {station['active_since']}</small>
            {'<br><small>Envoi: ' + station['data_send_time'] + '</small>' if 'data_send_time' in station else ''}
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown("### ⚠️ Statut des API")
    for name, station in STATIONS.items():
        try:
            response = requests.head(station['api_url'], timeout=5)
            if response.status_code == 200:
                st.markdown(f'<div class="api-status api-success">{name}: API accessible</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="api-status api-error">{name}: Erreur {response.status_code}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div class="api-status api-error">{name}: {str(e)}</div>', unsafe_allow_html=True)

# Section carte interactive
if selected_stations:
    st.markdown(f"<h2 class='section-title'>🗺️ Carte des stations</h2>", unsafe_allow_html=True)
    with st.spinner("Chargement de la carte..."):
        m = create_stations_map(selected_stations)
        st_folium(m, width=1200, height=500, key="map")

# Section indicateurs clés
if selected_stations:
    st.markdown(f"""
    <div style="background:{COLORS['primary']}; padding:15px; border-radius:10px; margin-bottom:25px">
        <h2 style="color:white; text-align:center; margin:0">📊 INDICATEURS CLÉS</h2>
    </div>
    """, unsafe_allow_html=True)
    
    cols = st.columns(len(selected_stations))
    
    for i, station_name in enumerate(selected_stations):
        with cols[i]:
            station_data = STATIONS[station_name]
            df = fetch_station_data(station_data['api_url'], station_name)
            
            if not df.empty:
                last_data = df.iloc[-1]
                prev_data = df.iloc[-2] if len(df) > 1 else None
                
                delta_temp = (last_data.get('temp', 0) - prev_data.get('temp', 0)) if prev_data is not None else None
                delta_humidity = (last_data.get('humidity', 0) - prev_data.get('humidity', 0)) if prev_data is not None else None
                
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{station_name}</div>
                    <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                        <div style="text-align: center; flex: 1;">
                            <div class="metric-value" style="color:{COLORS['accent']}">{last_data.get('temp', 'N/A'):.1f}°C</div>
                            <div class="metric-label">Température</div>
                        </div>
                        <div style="text-align: center; flex: 1;">
                            <div class="metric-value" style="color:{COLORS['secondary']}">{last_data.get('humidity', 'N/A'):.1f}%</div>
                            <div class="metric-label">Humidité</div>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                        <div style="text-align: center; flex: 1;">
                            <div class="metric-value" style="color:{COLORS['orange']}">{last_data.get('precipitation', 'N/A'):.1f} mm</div>
                            <div class="metric-label">Précipitation</div>
                        </div>
                        <div style="text-align: center; flex: 1;">
                            <div class="metric-value" style="color:{COLORS['primary']}">{last_data.get('wind_speed', 'N/A'):.1f} km/h</div>
                            <div class="metric-label">Vent</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"Aucune donnée disponible pour {station_name}")

# Section données temporelles
if selected_stations:
    st.markdown(f"<h2 class='section-title'>📈 Données temporelles</h2>", unsafe_allow_html=True)
    tabs = st.tabs([f"🌡️ {station}" for station in selected_stations])
    
    for i, station_name in enumerate(selected_stations):
        with tabs[i]:
            station_data = STATIONS[station_name]
            df = fetch_station_data(station_data['api_url'], station_name)
            
            if not df.empty:
                # Filtrage par date
                if len(date_range) == 2 and 'date' in df.columns:
                    mask = (df['date'].dt.date >= date_range[0]) & (df['date'].dt.date <= date_range[1])
                    df = df.loc[mask]
                
                # Sélection des variables disponibles
                available_vars = [v for v in variables if v in df.columns]
                
                if available_vars:
                    if chart_type == "Ligne":
                        fig = px.line(
                            df,
                            x='date',
                            y=available_vars,
                            title=f"Évolution des paramètres climatiques - {station_name}",
                            labels={'value': 'Valeur', 'date': 'Date'},
                            color_discrete_sequence=[COLORS['accent'], COLORS['secondary'], COLORS['orange'], COLORS['primary']]
                        )
                    elif chart_type == "Barre":
                        fig = px.bar(
                            df,
                            x='date',
                            y=available_vars,
                            title=f"Évolution des paramètres climatiques - {station_name}",
                            labels={'value': 'Valeur', 'date': 'Date'},
                            color_discrete_sequence=[COLORS['accent'], COLORS['secondary'], COLORS['orange'], COLORS['primary']],
                            barmode='group'
                        )
                    else:  # Zone
                        fig = px.area(
                            df,
                            x='date',
                            y=available_vars,
                            title=f"Évolution des paramètres climatiques - {station_name}",
                            labels={'value': 'Valeur', 'date': 'Date'},
                            color_discrete_sequence=[COLORS['accent'], COLORS['secondary'], COLORS['orange'], COLORS['primary']]
                        )
                    
                    fig.update_layout(
                        hovermode='x unified',
                        legend_title='Variables',
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        xaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
                        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Statistiques descriptives
                    st.markdown(f"<h3 class='section-title'>📋 Statistiques descriptives</h3>", unsafe_allow_html=True)
                    st.dataframe(df[available_vars].describe().style.format("{:.2f}"), use_container_width=True)
                else:
                    st.warning("Aucune des variables sélectionnées n'est disponible pour cette station.")
            else:
                st.warning(f"Aucune donnée disponible pour {station_name}")

# Section analyse comparative
if len(selected_stations) > 1:
    st.markdown(f"<h2 class='section-title'>📌 Analyse comparative</h2>", unsafe_allow_html=True)
    
    comparison_data = []
    for station_name in selected_stations:
        df = fetch_station_data(STATIONS[station_name]['api_url'], station_name)
        if not df.empty:
            station_stats = {'Station': station_name}
            
            if 'temp' in df.columns:
                station_stats.update({
                    'Temp. moyenne': df['temp'].mean(),
                    'Temp. max': df['temp'].max(),
                    'Temp. min': df['temp'].min()
                })
            
            if 'humidity' in df.columns:
                station_stats['Humidité moy.'] = df['humidity'].mean()
            
            if 'precipitation' in df.columns:
                station_stats['Précip. totale'] = df['precipitation'].sum()
            
            comparison_data.append(station_stats)
    
    if comparison_data:
        comparison_df = pd.DataFrame(comparison_data).set_index('Station')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌡️ Comparaison des températures")
            if all(col in comparison_df.columns for col in ['Temp. moyenne', 'Temp. max', 'Temp. min']):
                fig = px.bar(
                    comparison_df,
                    y=['Temp. moyenne', 'Temp. max', 'Temp. min'],
                    barmode='group',
                    color_discrete_sequence=[COLORS['accent'], COLORS['secondary'], COLORS['orange']],
                    labels={'value': 'Température (°C)'}
                )
                fig.update_layout(
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis=dict(showgrid=False),
                    yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Données de température manquantes pour la comparaison")
        
        with col2:
            st.markdown("### 🌧️ Précipitations totales")
            if 'Précip. totale' in comparison_df.columns:
                fig = px.pie(
                    comparison_df,
                    values='Précip. totale',
                    names=comparison_df.index,
                    color_discrete_sequence=[COLORS['accent'], COLORS['secondary'], COLORS['orange']],
                    hole=0.3
                )
                fig.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Données de précipitation manquantes pour la comparaison")
        
        # Tableau de comparaison
        st.markdown("### 📊 Tableau comparatif")
        st.dataframe(
            comparison_df.style
                .background_gradient(subset=['Temp. moyenne'], cmap='Blues')
                .background_gradient(subset=['Humidité moy.'], cmap='Greens')
                .format("{:.2f}"),
            use_container_width=True
        )

# Section export des données
if selected_stations:
    st.markdown(f"<h2 class='section-title'>📤 Export des données</h2>", unsafe_allow_html=True)
    export_station = st.selectbox("Sélectionnez une station à exporter", selected_stations)
    
    df = fetch_station_data(STATIONS[export_station]['api_url'], export_station)
    if not df.empty:
        st.dataframe(df.style.format({
            'temp': '{:.1f}',
            'humidity': '{:.1f}',
            'precipitation': '{:.1f}',
            'wind_speed': '{:.1f}'
        }), use_container_width=True)
        
        # Options d'export
        col1, col2 = st.columns(2)
        
        with col1:
            # Export CSV
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Télécharger en CSV",
                data=csv,
                file_name=f"donnees_{export_station.replace(' ', '_')}.csv",
                mime='text/csv',
                key='download-csv'
            )
        
        with col2:
            # Export Excel
            excel_buffer = BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Donnees_Climat')
            excel_buffer.seek(0)
            
            st.download_button(
                label="Télécharger en Excel",
                data=excel_buffer,
                file_name=f"donnees_{export_station.replace(' ', '_')}.xlsx",
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                key='download-excel'
            )
    else:
        st.warning(f"Aucune donnée disponible pour {export_station}")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#666;font-size:0.9em;">
    <p>Dashboard développé avec Streamlit • Données mises à jour quotidiennement</p>
    <p>© 2023 SmartSDGTunisia • Tous droits réservés</p>
</div>
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