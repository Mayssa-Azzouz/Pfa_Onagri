import streamlit as st
import folium
import pandas as pd
import numpy as np
from streamlit_folium import st_folium
import geopandas as gpd
from shapely.geometry import Point
import plotly.express as px
import matplotlib.pyplot as plt
from datetime import datetime

# --- Configuration de la page ---
st.set_page_config(
    layout="wide",
    page_title="SmartSDGTunisia - Données de Précipitations",
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
    /* Votre CSS existant reste inchangé */
    [data-testid="stHeader"] {{
        background-color: {COLORS['dark_blue']} !important;
        padding: 0;
    }}
    /* ... (conservez tout votre CSS existant) ... */
</style>
""", unsafe_allow_html=True)

# --- Chargement des données ---
@st.cache_data
def load_rainfall_data():
    # Charger les données depuis le fichier Excel
    notes = pd.read_excel("data/Rainfall_data.xlsx", sheet_name="Notes")
    data = pd.read_excel("data/Rainfall_data.xlsx", sheet_name="Data")
    
    # Nettoyer les données
    data = data.melt(id_vars=["Date"], var_name="Station_ID", value_name="Rainfall")
    data["Year"] = pd.to_datetime(data["Date"]).dt.year
    data["Month"] = pd.to_datetime(data["Date"]).dt.month
    data["Month_Name"] = pd.to_datetime(data["Date"]).dt.month_name()
    
    # Extraire les métadonnées des stations
    stations = notes.iloc[11:27, [3,4,5,6]].copy()
    stations.columns = ["Station_ID", "Name", "Lat", "Long"]
    stations["Station_ID"] = stations["Station_ID"].astype(str)
    
    # Fusionner avec les données de précipitation
    data = pd.merge(data, stations, on="Station_ID")
    
    return data, stations

rainfall_data, stations_data = load_rainfall_data()

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
        <h2 style="color: white; margin: 0; font-weight: 700;">Analyse des Précipitations</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
            Données historiques 1982-2018
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Filtres
    selected_years = st.slider(
        "Période",
        min_value=int(rainfall_data["Year"].min()),
        max_value=int(rainfall_data["Year"].max()),
        value=(2010, 2018)
    )
    
    selected_stations = st.multiselect(
        "Stations à inclure",
        options=stations_data["Name"].unique(),
        default=stations_data["Name"].unique()[:3]
    )
    
    analysis_type = st.radio(
        "Type d'analyse",
        options=["Annuelle", "Mensuelle", "Saisonnière"]
    )

# --- En-tête Principal ---
st.markdown(f"""
<div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
    <h1 style="color: {COLORS['dark_blue']}; margin: 0; text-align: center; font-weight: 700;">
        🌧️ Données de Précipitations en Tunisie
    </h1>
    <p style="color: {COLORS['dark_blue']}90; text-align: center; margin: 10px 0 0 0; font-size: 16px;">
        Analyse des données historiques (1982-2018) pour les gouvernorats de Kairouan et Siliana
    </p>
</div>
""", unsafe_allow_html=True)

# --- Section KPI Nationaux ---
st.markdown(f"""
<div style="background:{COLORS['dark_blue']}; padding:15px; border-radius:10px; margin-bottom:25px">
    <h2 style="color:white; text-align:center; margin:0">📊 INDICATEURS GLOBAUX</h2>
</div>
""", unsafe_allow_html=True)

# Calcul des KPI
filtered_data = rainfall_data[
    (rainfall_data["Year"] >= selected_years[0]) & 
    (rainfall_data["Year"] <= selected_years[1]) &
    (rainfall_data["Name"].isin(selected_stations))
]

total_rainfall = filtered_data["Rainfall"].sum()
avg_annual = filtered_data.groupby("Year")["Rainfall"].sum().mean()
max_month = filtered_data.groupby(["Year", "Month"])["Rainfall"].sum().max()
min_month = filtered_data.groupby(["Year", "Month"])["Rainfall"].sum().min()

# Ligne 1 - KPI Principaux
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['sky_blue']}; text-align:center">
        <h3>🌧 Précipitations totales</h3>
        <h1 style="color:{COLORS['sky_blue']}">{total_rainfall:,.0f} mm</h1>
        <p>Sur {selected_years[1]-selected_years[0]+1} années</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['mint_green']}; text-align:center">
        <h3>📅 Moyenne annuelle</h3>
        <h1 style="color:{COLORS['mint_green']}">{avg_annual:,.0f} mm</h1>
        <p>Par année</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['vivid_orange']}; text-align:center">
        <h3>⬆️ Maximum mensuel</h3>
        <h1 style="color:{COLORS['vivid_orange']}">{max_month:,.0f} mm</h1>
        <p>Record sur la période</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['raspberry_pink']}; text-align:center">
        <h3>⬇️ Minimum mensuel</h3>
        <h1 style="color:{COLORS['raspberry_pink']}">{min_month:,.0f} mm</h1>
        <p>Record sur la période</p>
    </div>
    """, unsafe_allow_html=True)

# --- Section Visualisation ---
st.markdown("---")

# Carte et Analyse Locale
col_map, col_analysis = st.columns([2, 1], gap="medium")

with col_map:
    st.markdown(f"<h2 class='section-title'>🗺️ Carte des Stations Météo</h2>", unsafe_allow_html=True)
    
    # Création de la carte
    m = folium.Map(
        location=[35.5, 9.5], 
        zoom_start=8, 
        tiles="cartodbpositron"
    )
    
    # Ajouter les stations
    for idx, row in stations_data.iterrows():
        folium.Marker(
            location=[row["Lat"], row["Long"]],
            popup=f"<b>{row['Name']}</b><br>ID: {row['Station_ID']}",
            tooltip=row["Name"],
            icon=folium.Icon(color="blue", icon="cloud")
        ).add_to(m)
    
    # Affichage de la carte
    map_data = st_folium(
        m, 
        height=600, 
        width="100%", 
        returned_objects=["last_object_clicked"]
    )
    
    # Gestion du clic sur la carte
    selected_station = None
    if map_data.get("last_object_clicked"):
        clicked = map_data["last_object_clicked"]
        try:
            lat, lng = clicked["lat"], clicked["lng"]
            selected_station = stations_data[
                (stations_data["Lat"] == lat) & 
                (stations_data["Long"] == lng)
            ].iloc[0]["Name"]
            st.session_state.selected_station = selected_station
        except:
            pass

with col_analysis:
    st.markdown("""
    <div class="local-kpi-container">
        <div class="local-kpi-title">📊 ANALYSE LOCALE</div>
    """, unsafe_allow_html=True)
    
    # Sélection de la station
    station_names = stations_data["Name"].unique()
    selected_station = st.selectbox(
        "Sélectionnez une station",
        options=station_names,
        index=0 if "selected_station" not in st.session_state 
              else list(station_names).index(st.session_state.get("selected_station", station_names[0]))
    )
    st.session_state.selected_station = selected_station
    
    # Filtrage des données
    station_data = rainfall_data[
        (rainfall_data["Name"] == selected_station) &
        (rainfall_data["Year"] >= selected_years[0]) &
        (rainfall_data["Year"] <= selected_years[1])
    ]
    
    if not station_data.empty:
        # KPI locaux
        station_avg = station_data["Rainfall"].mean()
        station_max = station_data["Rainfall"].max()
        station_min = station_data["Rainfall"].min()
        
        col_kpi1, col_kpi2 = st.columns(2)
        
        with col_kpi1:
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Moyenne mensuelle</div>
                <div class="local-kpi-value" style="color:{COLORS['sky_blue']}">{station_avg:.1f} mm</div>
                <div class="local-kpi-comparison">
                    vs {avg_annual:.1f} mm (moyenne globale)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with col_kpi2:
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Maximum enregistré</div>
                <div class="local-kpi-value" style="color:{COLORS['vivid_orange']}">{station_max:.1f} mm</div>
                <div class="local-kpi-comparison">
                    {station_max/max_month*100:.1f}% du record global
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Visualisation temporelle
        st.markdown(f"<h3 class='section-title'>📈 Tendances pour {selected_station}</h3>", unsafe_allow_html=True)
        
        if analysis_type == "Annuelle":
            annual_data = station_data.groupby("Year")["Rainfall"].sum().reset_index()
            fig = px.line(
                annual_data, 
                x="Year", 
                y="Rainfall",
                title=f"Précipitations annuelles ({selected_years[0]}-{selected_years[1]})",
                labels={"Rainfall": "Précipitations (mm)", "Year": "Année"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif analysis_type == "Mensuelle":
            monthly_avg = station_data.groupby("Month_Name")["Rainfall"].mean().reset_index()
            fig = px.bar(
                monthly_avg,
                x="Month_Name",
                y="Rainfall",
                title="Moyenne mensuelle",
                labels={"Rainfall": "Précipitations (mm)", "Month_Name": "Mois"},
                category_orders={"Month_Name": ["January", "February", "March", "April", "May", "June", 
                                             "July", "August", "September", "October", "November", "December"]}
            )
            st.plotly_chart(fig, use_container_width=True)
            
        elif analysis_type == "Saisonnière":
            # Définir les saisons
            def get_season(month):
                if month in [12, 1, 2]: return "Hiver"
                elif month in [3, 4, 5]: return "Printemps"
                elif month in [6, 7, 8]: return "Été"
                else: return "Automne"
            
            season_data = station_data.copy()
            season_data["Saison"] = season_data["Month"].apply(get_season)
            seasonal_avg = season_data.groupby("Saison")["Rainfall"].mean().reset_index()
            
            fig = px.pie(
                seasonal_avg,
                names="Saison",
                values="Rainfall",
                title="Répartition saisonnière",
                color="Saison",
                color_discrete_map={
                    "Hiver": COLORS["sky_blue"],
                    "Printemps": COLORS["mint_green"],
                    "Été": COLORS["vivid_orange"],
                    "Automne": COLORS["raspberry_pink"]
                }
            )
            st.plotly_chart(fig, use_container_width=True)

# --- Section Analyse Comparative ---
st.markdown("---")
st.markdown(f"<h2 class='section-title'>📊 Comparaison entre Stations</h2>", unsafe_allow_html=True)

if len(selected_stations) > 1:
    compare_data = rainfall_data[
        (rainfall_data["Name"].isin(selected_stations)) &
        (rainfall_data["Year"] >= selected_years[0]) &
        (rainfall_data["Year"] <= selected_years[1])
    ]
    
    # Comparaison annuelle
    annual_compare = compare_data.groupby(["Year", "Name"])["Rainfall"].sum().reset_index()
    fig = px.line(
        annual_compare,
        x="Year",
        y="Rainfall",
        color="Name",
        title="Comparaison annuelle entre stations",
        labels={"Rainfall": "Précipitations (mm)", "Year": "Année"}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Comparaison mensuelle moyenne
    monthly_compare = compare_data.groupby(["Month_Name", "Name"])["Rainfall"].mean().reset_index()
    fig = px.bar(
        monthly_compare,
        x="Month_Name",
        y="Rainfall",
        color="Name",
        barmode="group",
        title="Comparaison mensuelle moyenne",
        labels={"Rainfall": "Précipitations (mm)", "Month_Name": "Mois"},
        category_orders={"Month_Name": ["January", "February", "March", "April", "May", "June", 
                                     "July", "August", "September", "October", "November", "December"]}
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Sélectionnez au moins 2 stations pour la comparaison")

# --- Section Données Brutes ---
st.markdown("---")
st.markdown(f"<h2 class='section-title'>📋 Données Brutes</h2>", unsafe_allow_html=True)

show_raw_data = st.checkbox("Afficher les données brutes")
if show_raw_data:
    st.dataframe(
        rainfall_data,
        column_config={
            "Date": "Date",
            "Station_ID": "ID Station",
            "Rainfall": st.column_config.NumberColumn("Précipitations (mm)", format="%.1f"),
            "Name": "Nom de la station",
            "Lat": "Latitude",
            "Long": "Longitude"
        },
        hide_index=True,
        use_container_width=True
    )