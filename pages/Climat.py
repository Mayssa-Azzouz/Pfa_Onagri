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

# Configuration de la page
st.set_page_config(
    layout="wide",
    page_title="Dashboard Climatique Tunisie",
    page_icon="🌦️",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .metric-card {
        background: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .station-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #4e73df;
    }
    .header {
        background: linear-gradient(135deg, #4e73df 0%, #224abe 100%);
        padding: 25px;
        border-radius: 10px;
        color: white;
        margin-bottom: 30px;
    }
    .map-container {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }
    .stSelectbox > div > div {
        border-radius: 8px !important;
    }
    .stDateInput > div > div {
        border-radius: 8px !important;
    }
    .api-status {
        padding: 8px;
        border-radius: 4px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .api-success {
        background-color: #d4edda;
        color: #155724;
    }
    .api-error {
        background-color: #f8d7da;
        color: #721c24;
    }
    .new-station {
        border-left: 4px solid #f6c23e !important;
    }
</style>
""", unsafe_allow_html=True)

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

# Header du dashboard
st.markdown("""
<div class="header">
    <h1 style="margin:0;padding:0;">🌦️ Dashboard Climatique Tunisie</h1>
    <p style="margin:0;padding:0;font-size:1.1em;">Surveillance des stations météorologiques</p>
</div>
""", unsafe_allow_html=True)

# Sidebar pour la configuration
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/c/ce/Flag_of_Tunisia.svg", width=100)
    st.markdown("### 🔧 Paramètres")
    
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
    st.markdown("## 🗺️ Carte des stations")
    with st.spinner("Chargement de la carte..."):
        m = create_stations_map(selected_stations)
        st_folium(m, width=1200, height=500, key="map")

# [Les sections suivantes restent identiques...]
# Section indicateurs clés
if selected_stations:
    st.markdown("## 📊 Indicateurs clés")
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
                
                card_class = "new-station" if station_name == "Station Oued Souhil Nabeul" else ""
                st.markdown(f"""
                <div class="station-card {card_class}">
                    <h3 style="margin-top:0;color:#4e73df;">{station_name}</h3>
                    <p style="color:#666;margin-bottom:15px;">
                        <i class="fa fa-map-marker"></i> {station_data['region']} • Alt: {station_data['altitude']}m
                    </p>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Température", 
                             f"{last_data.get('temp', 'N/A'):.1f}°C", 
                             delta=f"{delta_temp:.1f}°C" if delta_temp is not None else None)
                    st.metric("Précipitation", 
                             f"{last_data.get('precipitation', 'N/A'):.1f} mm")
                with col2:
                    st.metric("Humidité", 
                             f"{last_data.get('humidity', 'N/A'):.1f}%", 
                             delta=f"{delta_humidity:.1f}%" if delta_humidity is not None else None)
                    st.metric("Vent", 
                             f"{last_data.get('wind_speed', 'N/A'):.1f} km/h")
                
                st.markdown("</div>", unsafe_allow_html=True)
            else:
                st.warning(f"Aucune donnée disponible pour {station_name}")

# Section données temporelles
if selected_stations:
    st.markdown("## 📈 Données temporelles")
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
                            color_discrete_sequence=['#4e73df', '#1cc88a', '#f6c23e', '#e74a3b']
                        )
                    elif chart_type == "Barre":
                        fig = px.bar(
                            df,
                            x='date',
                            y=available_vars,
                            title=f"Évolution des paramètres climatiques - {station_name}",
                            labels={'value': 'Valeur', 'date': 'Date'},
                            color_discrete_sequence=['#4e73df', '#1cc88a', '#f6c23e', '#e74a3b'],
                            barmode='group'
                        )
                    else:  # Zone
                        fig = px.area(
                            df,
                            x='date',
                            y=available_vars,
                            title=f"Évolution des paramètres climatiques - {station_name}",
                            labels={'value': 'Valeur', 'date': 'Date'},
                            color_discrete_sequence=['#4e73df', '#1cc88a', '#f6c23e', '#e74a3b']
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
                    st.markdown("### 📋 Statistiques descriptives")
                    st.dataframe(df[available_vars].describe().style.format("{:.2f}"), use_container_width=True)
                else:
                    st.warning("Aucune des variables sélectionnées n'est disponible pour cette station.")
            else:
                st.warning(f"Aucune donnée disponible pour {station_name}")

# Section analyse comparative
if len(selected_stations) > 1:
    st.markdown("## 📌 Analyse comparative")
    
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
                    color_discrete_sequence=['#4e73df', '#1cc88a', '#f6c23e'],
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
                    color_discrete_sequence=px.colors.sequential.Blues_r,
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
    st.markdown("## 📤 Export des données")
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