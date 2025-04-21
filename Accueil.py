import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="SmartSDGTunisia", page_icon="🇹🇳", layout="wide")

# 🎨 Palette de couleurs
COLORS = {
    "sky_blue": "#00B4D8",
    "mint_green": "#43AA8B",
    "vivid_orange": "#F8961E",
    "raspberry_pink": "#F15BB5",
    "soft_purple": "#9B5DE5",
    "light_gray": "#F0F0F0",
    "dark_blue": "#1A1A2E"
}

# 💡 CSS personnalisé
st.markdown(f"""
<style>
    /* Style de la navbar */
    div[data-testid="stHorizontalBlock"] {{
        background-color: {COLORS['dark_blue']};
        padding: 10px 15px;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }}
    
    div[role="radiogroup"] > label {{
        background-color: transparent;
        color: white !important;
        padding: 8px 20px;
        margin: 0 5px;
        border-radius: 20px;
        transition: all 0.3s ease;
        border: 1px solid {COLORS['sky_blue']};
    }}
    
    div[role="radiogroup"] > label:hover {{
        background-color: {COLORS['sky_blue']}40;
        transform: translateY(-2px);
    }}
    
    div[role="radiogroup"] > label[data-selected="true"] {{
        background-color: {COLORS['vivid_orange']} !important;
        border-color: {COLORS['vivid_orange']};
        font-weight: bold;
        box-shadow: 0 4px 8px {COLORS['vivid_orange']}30;
    }}
    
    /* Style global */
    .main-container {{
        max-width: 1200px;
        margin: 0 auto;
    }}
    
    .section {{
        margin-bottom: 40px;
    }}
    
    .section-title {{
        color: {COLORS['dark_blue']};
        border-bottom: 2px solid {COLORS['vivid_orange']};
        padding-bottom: 8px;
        margin-bottom: 20px;
    }}
    
    .card {{
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border-left: 5px solid {COLORS['sky_blue']};
        margin-bottom: 20px;
        transition: transform 0.3s ease;
    }}
    
    .card:hover {{
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }}
    
    .footer {{
        margin-top: 50px;
        padding: 15px;
        text-align: center;
        color: {COLORS['dark_blue']};
        font-size: 13px;
        border-top: 1px solid {COLORS['light_gray']};
    }}
</style>
""", unsafe_allow_html=True)

# 🚀 Barre de navigation
selected_page = st.radio(
    "Navigation",
    options=["🏠 Accueil",  "🌧️ Pluviométrie", "🌍 Thèmes ODD", "🌡️ Climat", "📊 Données", "ℹ️ À propos"],
    horizontal=True,
    key="navbar",
    label_visibility="collapsed"
)

# Conteneur principal
with st.container():
    st.markdown("<div class='main-container'>", unsafe_allow_html=True)
    
    # ==================== PAGE D'ACCUEIL ====================
    if selected_page == "🏠 Accueil":
        # Section 1: En-tête
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.title("SmartSDGTunisia")
        st.markdown("""
        <div style='font-size: 1.1rem; line-height: 1.6; margin-bottom: 30px;'>
            Plateforme de suivi des Objectifs de Développement Durable en Tunisie.
            Visualisez les données clés et les progrès accomplis.
        </div>
        """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Section 2: Métriques
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.markdown("<h2 class='section-title'>Indicateurs Clés</h2>", unsafe_allow_html=True)
        
        cols = st.columns(4)
        metrics = [
            {"title": "Pauvreté", "value": "15.2%", "odd": "ODD 1", "color": COLORS["raspberry_pink"], "icon": "💰"},
            {"title": "Éducation", "value": "89%", "odd": "ODD 4", "color": COLORS["soft_purple"], "icon": "📚"},
            {"title": "Énergie", "value": "78%", "odd": "ODD 7", "color": COLORS["vivid_orange"], "icon": "⚡"},
            {"title": "Climat", "value": "62", "odd": "ODD 13", "color": COLORS["mint_green"], "icon": "🌍"},
        ]
        
        for col, metric in zip(cols, metrics):
            with col:
                st.markdown(f"""
                    <div class="card">
                        <h3>{metric['icon']} {metric['title']}</h3>
                        <p style='font-size: 24px; color: {metric['color']}; margin: 10px 0;'>{metric['value']}</p>
                        <p style='color: {COLORS['dark_blue']};'>{metric['odd']}</p>
                    </div>
                """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Section 3: Carte
        st.markdown("<div class='section'>", unsafe_allow_html=True)
        st.markdown("<h2 class='section-title'>Carte Interactive</h2>", unsafe_allow_html=True)
        
        tunisia_data = pd.DataFrame({
            'Région': ['Tunis', 'Sfax', 'Sousse', 'Kairouan', 'Gabès'],
            'Latitude': [36.8, 34.74, 35.83, 35.68, 33.88],
            'Longitude': [10.18, 10.76, 10.64, 10.1, 10.1],
            'Score ODD': [75, 68, 72, 65, 60],
            'Indicateur Clé': ['Éducation', 'Emploi', 'Santé', 'Agriculture', 'Environnement']
        })
        
        fig = px.scatter_mapbox(
            tunisia_data,
            lat="Latitude",
            lon="Longitude",
            hover_name="Région",
            hover_data=["Score ODD", "Indicateur Clé"],
            size="Score ODD",
            color="Indicateur Clé",
            zoom=5.5,
            size_max=25,
            height=500,
            color_discrete_sequence=[
                COLORS['sky_blue'], COLORS['mint_green'],
                COLORS['vivid_orange'], COLORS['raspberry_pink'], COLORS['soft_purple']
            ]
        )
        fig.update_layout(mapbox_style="carto-positron", margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    # ==================== AUTRES PAGES ====================
    elif selected_page == "🌧️ Pluviométrie":
        st.switch_page("pages/Pluviometrie.py") 
    elif selected_page == "🌍 Thèmes ODD":
        st.title("Thèmes ODD")
        st.write("Contenu des différents thèmes ODD...")
        
    elif selected_page == "🌡️ Climat":
        st.title("Indicateurs Climatiques")
        st.write("Données et visualisations sur le climat...")
        
    elif selected_page == "📊 Données":
        st.title("Base de Données")
        st.write("Accès aux données complètes...")
        
    elif selected_page == "ℹ️ À propos":
        st.title("À Propos")
        st.markdown("""
        <div style='line-height: 1.6;'>
            <h3>Notre Mission</h3>
            <p>Fournir des données accessibles pour le développement durable en Tunisie.</p>
            
            <h3>Équipe</h3>
            <p>Description de l'équipe et des partenaires...</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Pied de page
    st.markdown("<div class='footer'>© 2023 SmartSDGTunisia - Plateforme ODD Tunisie</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # Fermeture du main-container