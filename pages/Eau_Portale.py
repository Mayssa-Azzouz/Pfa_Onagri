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

# 🎨 Palette de couleurs cohérente
COLORS = {
    "water_blue": "#00B4D8",
    "deep_blue": "#1A1A2E",
    "light_blue": "#90E0EF",
    "teal": "#0077B6",
    "light_gray": "#F0F0F0",
    "vivid_blue": "#3A86FF"
}

# --- CSS Personnalisé ---
st.markdown(f"""
<style>
    /* Style global existant */
    [data-testid="stHeader"] {{
        background-color: {COLORS['deep_blue']} !important;
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
        color: {COLORS['deep_blue']};
        font-weight: 600;
    }}
    
    .card {{
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
        border-left: 4px solid {COLORS['water_blue']};
        transition: all 0.3s ease;
    }}
    
    .card:hover {{
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.12);
    }}
    
    .section-title {{
        color: {COLORS['deep_blue']};
        border-bottom: 2px solid {COLORS['water_blue']};
        padding-bottom: 8px;
        margin-bottom: 20px;
    }}
    
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['deep_blue']} !important;
    }}
    
    .sidebar .sidebar-content {{
        background: linear-gradient(180deg, {COLORS['deep_blue']}, #1E1E3C) !important;
        padding: 20px 15px !important;
    }}
    
    .folium-map {{
        border-radius: 12px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        border: 1px solid {COLORS['light_gray']} !important;
    }}
    
    .local-kpi-container {{
        background: rgba(255, 255, 255, 0.95);
        border-radius: 16px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin-bottom: 25px;
        border: 1px solid rgba(0,0,0,0.05);
    }}
    
    .local-kpi-title {{
        color: {COLORS['deep_blue']};
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
        background: {COLORS['water_blue']};
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
        color: {COLORS['deep_blue']};
        text-align: center;
        padding: 5px;
        border-radius: 12px;
        background: rgba(0,180,216,0.1);
    }}
</style>
""", unsafe_allow_html=True)

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
        background: linear-gradient(135deg, {COLORS['teal']}, {COLORS['water_blue']});
        padding: 25px;
        border-radius: 12px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    ">
        <h2 style="color: white; margin: 0; font-weight: 700;">Eau Potable</h2>
        <p style="color: rgba(255,255,255,0.9); margin: 5px 0 0 0; font-size: 14px;">
            Consommation mensuelle par gouvernorat
        </p>
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
<div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
    <h1 style="color: {COLORS['deep_blue']}; margin: 0; text-align: center; font-weight: 700;">
        💧 SmartSDGTunisia - Consommation d'Eau Potable
    </h1>
    <p style="color: {COLORS['deep_blue']}90; text-align: center; margin: 10px 0 0 0; font-size: 16px;">
        Analyse de la consommation mensuelle par gouvernorat
    </p>
</div>
""", unsafe_allow_html=True)

# --- Section KPI Nationaux ---
st.markdown(f"""
<div style="background:{COLORS['deep_blue']}; padding:15px; border-radius:10px; margin-bottom:25px">
    <h2 style="color:white; text-align:center; margin:0">📊 INDICATEURS NATIONAUX</h2>
</div>
""", unsafe_allow_html=True)

# Ligne 1 - KPI Principaux
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['water_blue']}; text-align:center">
        <h3>💧 Consommation annuelle</h3>
        <h1 style="color:{COLORS['water_blue']}">{total_annual:,.0f}</h1>
        <p>m³ (milliers)</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['light_blue']}; text-align:center">
        <h3>📅 Moyenne mensuelle</h3>
        <h1 style="color:{COLORS['light_blue']}">{avg_monthly:,.0f}</h1>
        <p>m³ (milliers)</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['teal']}; text-align:center">
        <h3>🔥 Mois de pic</h3>
        <h1 style="color:{COLORS['teal']}">{max_month}</h1>
        <p>{max_value:,.0f} m³ (milliers)</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="card" style="border-left: 4px solid {COLORS['vivid_blue']}; text-align:center">
        <h3>🌡️ Variation saisonnière</h3>
        <h1 style="color:{COLORS['vivid_blue']}">+{(max_value/avg_monthly-1)*100:.0f}%</h1>
        <p>Pic vs moyenne</p>
    </div>
    """, unsafe_allow_html=True)

# Ligne 2 - Top 3
st.markdown("<br>", unsafe_allow_html=True)
col5, col6 = st.columns(2)

with col5:
    st.markdown(f"""
    <div class="card">
        <h3 style="color:{COLORS['deep_blue']}">🏆 Top 3 Consommation</h3>
        <table style="width:100%">
            <tr><th>Gouvernorat</th><th>Moyenne (m³)</th><th>Part</th></tr>
            <tr><td>{top_gouvernorats.iloc[0,0]}</td><td>{top_gouvernorats.iloc[0,1]:,.0f}</td><td>{(top_gouvernorats.iloc[0,1]/avg_monthly/24*100):.1f}%</td></tr>
            <tr><td>{top_gouvernorats.iloc[1,0]}</td><td>{top_gouvernorats.iloc[1,1]:,.0f}</td><td>{(top_gouvernorats.iloc[1,1]/avg_monthly/24*100):.1f}%</td></tr>
            <tr><td>{top_gouvernorats.iloc[2,0]}</td><td>{top_gouvernorats.iloc[2,1]:,.0f}</td><td>{(top_gouvernorats.iloc[2,1]/avg_monthly/24*100):.1f}%</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

with col6:
    # Évolution mensuelle
    monthly_totals = df_water[['Janvier', 'Fevrier', 'Mars', 'Avril', 'Mai', 'Juin', 
                             'Juillet', 'Aout', 'Septembre', 'Octobre', 'Novembre', 'Decembre']].sum()
    
    st.markdown(f"""
    <div class="card">
        <h3 style="color:{COLORS['deep_blue']}">📈 Évolution mensuelle</h3>
        <div style="height:200px; display:flex; align-items:center; justify-content:center;">
            <img src="https://quickchart.io/chart?c={{type:'line',data:{{labels:['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'], datasets:[{{label:'Consommation (m³)', data:{monthly_totals.tolist()}, borderColor:'{COLORS['water_blue']}', fill:false}}]}}}}" 
                 style="max-width:100%; max-height:180px;">
        </div>
    </div>
    """, unsafe_allow_html=True)

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
        fill_color="Blues",
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
    gouvernorats = sorted(df_water['gouvernorat'].unique().tolist())
    
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
                <div class="local-kpi-value" style="color:{COLORS['water_blue']}">{gouv_data[selected_month]:,.0f}</div>
                <div class="local-kpi-comparison">
                    {(gouv_data[selected_month]/df_water[selected_month].sum()*100):.1f}% du national
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Moyenne annuelle</div>
                <div class="local-kpi-value" style="color:{COLORS['teal']}">{monthly_data.mean():,.0f}</div>
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
                <div class="local-kpi-value" style="color:{COLORS['vivid_blue']}">{max_local_month}</div>
                <div class="local-kpi-comparison">
                    {monthly_data[max_local_month]:,.0f} m³ (+{(monthly_data[max_local_month]/monthly_data.mean()-1)*100:.0f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="local-kpi-card">
                <div class="local-kpi-label">Mois le plus bas</div>
                <div class="local-kpi-value" style="color:{COLORS['light_blue']}">{min_local_month}</div>
                <div class="local-kpi-comparison">
                    {monthly_data[min_local_month]:,.0f} m³ ({(monthly_data[min_local_month]/monthly_data.mean()-1)*100:.0f}%)
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Classement national
        rank_month = int(df_water[selected_month].rank(ascending=False, method='min').loc[df_water['gouvernorat'] == st.session_state.selected_gouv].values[0])
        rank_annual = int(df_water['Moyenne_annuelle'].rank(ascending=False, method='min').loc[df_water['gouvernorat'] == st.session_state.selected_gouv].values[0])
        
        st.markdown(f"""
        <div class="local-kpi-card" style="text-align:center; background: rgba(26,26,46,0.03);">
            <div style="font-size:0.9rem; color:#555;">Classement National</div>
            <div style="display:flex; justify-content:space-around; margin-top:10px;">
                <div>
                    <div style="font-size:0.8rem;">{selected_month}</div>
                    <div style="font-size:1.2rem; font-weight:700; color:{COLORS['deep_blue']}">#{rank_month}</div>
                </div>
                <div>
                    <div style="font-size:0.8rem;">Annuel</div>
                    <div style="font-size:1.2rem; font-weight:700; color:{COLORS['deep_blue']}">#{rank_annual}</div>
                </div>
            </div>
        </div>
        </div>  <!-- Fermeture du container -->
        """, unsafe_allow_html=True)
        
        # Graphique d'évolution mensuelle
        st.markdown(f"<h2 class='section-title'>📈 Évolution Mensuelle</h2>", unsafe_allow_html=True)
        st.line_chart(
            monthly_data,
            use_container_width=True,
            color=COLORS['water_blue']
        )
    else:
        st.markdown("""
        <div style="text-align:center; padding:30px; color:#666;">
            Sélectionnez un gouvernorat pour voir les statistiques locales
        </div>
        </div>  <!-- Fermeture du container -->
        """, unsafe_allow_html=True)

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