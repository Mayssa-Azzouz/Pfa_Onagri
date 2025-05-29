import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# --- Configuration de la page ---
st.set_page_config(
    layout="wide",
    page_title="ONAGRI - Données Pluviométriques",
    page_icon="🌧️",
    initial_sidebar_state="auto"
)

# 🎨 Palette de couleurs ONAGRI améliorée
COLORS = {
    "primary": "#1E6C41",      # Vert foncé
    "secondary": "#2E7D32",    # Vert
    "accent": "#4CAF50",       # Vert clair
    "background": "#F5FBF5",   # Fond très clair
    "text": "#263238",         # Texte foncé
    "white": "#FFFFFF",
    "dark_green": "#2E7D32",
    "light_green": "#78C27D",
    "lighter_green": "#C8E6C9",
    "gradient_start": "#1E6C41",
    "gradient_end": "#4CAF50",
    "light_text": "#607D8B",
    "accent_orange": "#FF6D00",
    "accent_blue": "#1976D2"
}

# --- CSS Personnalisé ---
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
        padding-top: 5rem;
        padding-bottom: 2rem;
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
        color: {COLORS['primary']};
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
        color: {COLORS['text']};
        margin: 10px 0;
    }}
    
    .card-footer {{
        margin-top: auto;
        color: {COLORS['light_text']};
        font-size: 0.9rem;
    }}
    
    /* Sidebar améliorée */
    [data-testid="stSidebar"] {{
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
    .stSidebar .stTextInput {{
        background-color: rgba(255,255,255,0.9) !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
    }}
    
    .stSidebar label {{
        color: white !important;
        font-weight: 500 !important;
    }}
    
    .stButton>button {{
        background: linear-gradient(135deg, {COLORS['accent_orange']}, #FFA000) !important;
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
    
    /* Conteneur KPI local */
    .local-kpi-container {{
        background: white;
        border-radius: 16px;
        padding: 25px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 30px;
    }}
    
    .local-kpi-title {{
        color: {COLORS['primary']};
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
        color: {COLORS['text']};
        font-weight: 500;
        font-size: 0.95rem;
    }}
    
    .local-kpi-value {{
        color: {COLORS['primary']};
        font-weight: 700;
        font-size: 1.4rem;
        margin: 5px 0;
    }}
    
    /* Carte */
    .folium-map {{
        border-radius: 16px !important;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
        border: none !important;
        overflow: hidden;
    }}
    
    /* Graphiques */
    .plotly-graph {{
        border-radius: 16px;
        overflow: hidden;
    }}
    
    /* En-tête de section */
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
    
    /* Titres de section */
    .section-title {{
        color: {COLORS['primary']};
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
    
    /* Masquer les éléments Streamlit */
    #MainMenu, footer, header {{
        visibility: hidden;
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
        
        [data-testid="stSidebar"] {{
            padding: 0.5rem !important;
        }}
        
        .main-content {{
            padding-top: 7rem;
        }}
    }}
</style>
""", unsafe_allow_html=True)

# --- Barre de navigation ONAGRI modernisée ---
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

# --- Chargement des données ---
@st.cache_data
def load_data():
    df = pd.read_excel("Rainfall_data.xlsx", sheet_name="Data")
    df.columns = [str(col) for col in df.columns]
    
    stations_df = pd.read_excel("Rainfall_data.xlsx", sheet_name="Note")
    stations_df = stations_df.rename(columns={"N": "ID", "Name": "Station"})
    
    numeric_cols = [col for col in df.columns if col != "Date"]
    df_mean = df[numeric_cols].mean().reset_index()
    df_mean.columns = ['ID', 'Valeur']
    df_mean['ID'] = df_mean['ID'].astype(int)
    
    merged_df = pd.merge(df_mean, stations_df, on="ID")
    return df, merged_df

# --- Affichage de la navbar ONAGRI ---
render_navbar("Pluviométrie")

# --- Contenu principal ---
df, merged_df = load_data()

# Section KPI - Header amélioré
st.markdown(f"""
<div class="section-header">
    <h1>📊 INDICATEURS PLUVIOMÉTRIQUES</h1>
    <p style="color:rgba(255,255,255,0.9); margin-top:10px;">
        Analyse des précipitations moyennes sur toutes les stations (1982-2018)
    </p>
</div>
""", unsafe_allow_html=True)

# Calcul des KPI
avg_rainfall = merged_df['Valeur'].mean()
max_rainfall = merged_df['Valeur'].max()
min_rainfall = merged_df['Valeur'].min()
station_count = len(merged_df)

# Ligne de KPI améliorée
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card">
        <div class="card-title"><span class="card-icon">🌧️</span> Précipitation moyenne</div>
        <div class="card-value">{avg_rainfall:.1f} mm</div>
        <div class="card-footer">Sur toutes les stations</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    max_station = merged_df.loc[merged_df['Valeur'].idxmax(), 'Station']
    st.markdown(f"""
    <div class="card">
        <div class="card-title"><span class="card-icon">⬆️</span> Maximum</div>
        <div class="card-value">{max_rainfall:.1f} mm</div>
        <div class="card-footer">Station: {max_station}</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    min_station = merged_df.loc[merged_df['Valeur'].idxmin(), 'Station']
    st.markdown(f"""
    <div class="card">
        <div class="card-title"><span class="card-icon">⬇️</span> Minimum</div>
        <div class="card-value">{min_rainfall:.1f} mm</div>
        <div class="card-footer">Station: {min_station}</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card">
        <div class="card-title"><span class="card-icon">📍</span> Stations</div>
        <div class="card-value">{station_count}</div>
        <div class="card-footer">Stations météorologiques</div>
    </div>
    """, unsafe_allow_html=True)

# --- Sidebar améliorée ---
with st.sidebar:
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, {COLORS['primary']}, {COLORS['secondary']});
        padding: 25px 20px;
        border-radius: 16px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    ">
        <div class="sidebar-title">🌧️ Données Pluviométriques</div>
        <div class="sidebar-subtitle">Analyse des précipitations (1982-2018)</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔎 Filtres")
    selected_year = st.slider(
        "Période d'analyse",
        1982, 2018, (2000, 2010),
        help="Sélectionnez la période à analyser"
    )
    
    st.markdown("### 📊 Options de visualisation")
    show_map = st.checkbox("Afficher la carte", value=True)
    show_stats = st.checkbox("Afficher les statistiques", value=True)
    
    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:rgba(255,255,255,0.7); font-size:0.9rem;">
        © 2023 ONAGRI - Observatoire National de l'Agriculture
    </div>
    """, unsafe_allow_html=True)

# --- Carte et Statistiques ---
if show_map or show_stats:
    st.markdown('<h2 class="section-title">📌 Visualisation Géographique</h2>', unsafe_allow_html=True)
    
    col_map, col_stats = st.columns([1, 1], gap="large")
    
    with col_map:
        if show_map:
            # Carte améliorée
            m = folium.Map(
                location=[merged_df['Lat'].mean(), merged_df['Long'].mean()], 
                zoom_start=7,
                tiles="cartodbpositron"
            )
            
            # Ajout des marqueurs avec une meilleure visualisation
            for idx, row in merged_df.iterrows():
                folium.CircleMarker(
                    location=[row['Lat'], row['Long']],
                    radius=8 + (row['Valeur']/10),
                    popup=f"""
                    <div style="font-family: Arial; width: 200px;">
                        <h4 style="color:{COLORS['primary']}; margin-bottom:5px;">{row['Station']}</h4>
                        <p><b>Précipitation moyenne:</b> {row['Valeur']:.1f} mm</p>
                        <p><b>Coordonnées:</b> {row['Lat']:.2f}°N, {row['Long']:.2f}°E</p>
                    </div>
                    """,
                    color=COLORS['primary'],
                    fill=True,
                    fill_color=COLORS['accent_orange'],
                    fill_opacity=0.7,
                    weight=1.5
                ).add_to(m)
            
            # Ajout d'un fond de carte plus esthétique
            folium.TileLayer(
                'https://{s}.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}{r}.png',
                attr='CartoDB.VoyagerLabelsUnder'
            ).add_to(m)
            
            st_folium(m, width="100%", height=500)

    with col_stats:
        if show_stats:
            st.markdown("""
            <div class="local-kpi-container">
                <div class="local-kpi-title">
                    <span style="margin-right:10px;">📊</span> STATISTIQUES PAR STATION
                </div>
            """, unsafe_allow_html=True)
            
            selected_station = st.selectbox(
                "Sélectionnez une station",
                options=merged_df['Station'].unique(),
                index=0,
                key="station_select"
            )
            
            station_data = merged_df[merged_df['Station'] == selected_station].iloc[0]
            
            col_kpi1, col_kpi2 = st.columns(2)
            
            with col_kpi1:
                st.markdown(f"""
                <div class="local-kpi-card">
                    <div class="local-kpi-label">Précipitation moyenne</div>
                    <div class="local-kpi-value">{station_data['Valeur']:.1f} mm</div>
                    <div style="font-size:0.9rem; color:{COLORS['light_text']};">
                        {(station_data['Valeur']/avg_rainfall*100):.1f}% de la moyenne nationale
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
            with col_kpi2:
                st.markdown(f"""
                <div class="local-kpi-card">
                    <div class="local-kpi-label">Coordonnées</div>
                    <div class="local-kpi-value">
                        {station_data['Lat']:.2f}°N, {station_data['Long']:.2f}°E
                    </div>
                    <div style="font-size:0.9rem; color:{COLORS['light_text']};">
                        ID: {station_data['ID']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            rank = int(merged_df['Valeur'].rank(ascending=False, method='min').loc[merged_df['Station'] == selected_station].values[0])
            st.markdown(f"""
            <div class="local-kpi-card" style="text-align:center; background: linear-gradient(135deg, {COLORS['gradient_start']}, {COLORS['gradient_end']});">
                <div style="color:white; font-weight:500; margin-bottom:5px;">Classement National</div>
                <div style="font-size:2rem; font-weight:700; color:white;">#{rank}</div>
                <div style="color:rgba(255,255,255,0.8); font-size:0.9rem;">sur {len(merged_df)} stations</div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"<h3 style='color:{COLORS['primary']}; margin-top:20px;'>📋 Fiche Technique</h3>", unsafe_allow_html=True)
            st.dataframe(
                station_data.to_frame().T, 
                hide_index=True, 
                use_container_width=True,
                column_config={
                    "ID": "ID",
                    "Valeur": st.column_config.NumberColumn("Précipitation (mm)", format="%.1f mm"),
                    "Station": "Nom",
                    "Lat": "Latitude",
                    "Long": "Longitude"
                }
            )

# --- Visualisation temporelle améliorée ---
st.markdown('<h2 class="section-title">📈 Évolution Temporelle</h2>', unsafe_allow_html=True)

selected_stations = st.multiselect(
    "Sélectionnez les stations à visualiser",
    options=merged_df['Station'].unique(),
    default=merged_df.nlargest(3, 'Valeur')['Station'].tolist(),
    key="stations_select"
)

if selected_stations:
    station_ids = merged_df[merged_df['Station'].isin(selected_stations)]['ID'].tolist()
    available_columns = [col for col in df.columns if col != 'Date']
    valid_station_ids = [str(id) for id in station_ids if str(id) in available_columns]
    
    if valid_station_ids:
        df_filtered = df[['Date'] + valid_station_ids]
        df_filtered = df_filtered.melt(id_vars='Date', var_name='ID', value_name='Précipitation')
        df_filtered['ID'] = df_filtered['ID'].astype(int)
        df_filtered = pd.merge(df_filtered, merged_df[['ID', 'Station']], on='ID')
        
        # Graphique amélioré
        fig = px.line(
            df_filtered, 
            x='Date', 
            y='Précipitation', 
            color='Station',
            color_discrete_sequence=[
                COLORS['primary'], 
                COLORS['accent_orange'], 
                COLORS['accent_blue'],
                COLORS['dark_green'],
                COLORS['light_text']
            ],
            labels={
                "Date": "Année",
                "Précipitation": "Précipitation (mm)",
                "Station": "Station"
            },
            template="plotly_white"
        )
        
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode="x unified",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            xaxis=dict(
                showgrid=True,
                gridcolor=COLORS['lighter_green'],
                title_font=dict(size=14)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor=COLORS['lighter_green'],
                title_font=dict(size=14)
            ),
            margin=dict(l=0, r=0, t=30, b=0)
        )
        
        fig.update_traces(
            line_width=2.5,
            hovertemplate="<b>%{x|%Y}</b><br>%{y:.1f} mm<extra></extra>"
        )
        
        st.plotly_chart(fig, use_container_width=True, className="plotly-graph")

# Fermeture de la div main-content
st.markdown("</div>", unsafe_allow_html=True)