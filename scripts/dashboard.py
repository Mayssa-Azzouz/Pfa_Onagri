import streamlit as st
import plotly.express as px
from scripts.arabic_utils import normalize_arabic

def show_dashboard(properties, df, graph_type):
    # Style CSS additionnel pour le dashboard
    st.markdown("""
        <style>
            .metric {
                background-color: #E6F3FF;
                border-radius: 10px;
                padding: 15px;
                border-left: 4px solid #1E90FF;
            }
            .stDataFrame {
                border-radius: 10px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .stAlert {
                border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    if not properties or df is None:
        st.info("ℹ️ Cliquez sur une délégation dans la carte pour afficher les données correspondantes")
        return
    
    del_ar = properties.get('del_ar')
    del_fr = properties.get('del_fr', 'Inconnu')
    
    # Header avec style amélioré
    st.markdown(f"""
        <div style='background-color:#E6F3FF; padding:15px; border-radius:10px; margin-bottom:20px;'>
            <h3 style='color:#1E90FF; margin:0;'>📊 Données pour: {del_fr} / {del_ar}</h3>
        </div>
    """, unsafe_allow_html=True)
    
    # Normalisation et recherche des stations
    normalized_del = normalize_arabic(del_ar)
    matching_stations = [
        station for station in df['station'].unique()
        if normalize_arabic(station) == normalized_del
    ]
    
    if not matching_stations:
        st.error(f"⚠️ Aucune station ne correspond à {del_ar}")
        return
    
    station_data = df[df['station'].isin(matching_stations)]
    
    if station_data.empty:
        st.warning("⚠️ Données pluviométriques non disponibles pour cette station")
        return
    
    # Metrics avec style amélioré
    latest = station_data.iloc[-1]
    cols = st.columns(3)
    with cols[0]:
        st.markdown(f"""
            <div class='metric'>
                <div style='font-size:14px; color:#555;'>Pluie du jour</div>
                <div style='font-size:24px; font-weight:bold; color:#1E90FF;'>{latest['Pluvio_du_jour']} mm</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[1]:
        st.markdown(f"""
            <div class='metric'>
                <div style='font-size:14px; color:#555;'>Cumul mensuel</div>
                <div style='font-size:24px; font-weight:bold; color:#3bdb6e;'>{latest['Cumul_du_mois']} mm</div>
            </div>
        """, unsafe_allow_html=True)
    
    with cols[2]:
        st.markdown(f"""
            <div class='metric'>
                <div style='font-size:14px; color:#555;'>Cumul période</div>
                <div style='font-size:24px; font-weight:bold; color:#6495ED;'>{latest['Cumul_periode']} mm</div>
            </div>
        """, unsafe_allow_html=True)
    
    # Graphique avec style amélioré
    st.markdown("---")
    st.markdown("### 📈 Visualisation des données")
    
    if graph_type == "Courbe":
        fig = px.line(
            station_data, 
            x='Date', 
            y='Pluvio_du_jour',
            title=f"Évolution de la pluviométrie à {del_fr}",
            color_discrete_sequence=["#1E90FF"],
            template="plotly_white"
        )
    elif graph_type == "Barres":
        fig = px.bar(
            station_data, 
            x='Date', 
            y='Pluvio_du_jour',
            title=f"Pluviométrie journalière à {del_fr}",
            color_discrete_sequence=["#3bdb6e"],
            template="plotly_white"
        )
    
    # Personnalisation du graphique
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis_title="Date",
        yaxis_title="Pluviométrie (mm)",
        hovermode="x unified",
        font=dict(family="sans serif", size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau de données avec style
    st.markdown("---")
    st.markdown("### 📋 Données brutes")
    st.dataframe(
        station_data.sort_values('Date', ascending=False),
        height=300,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date": st.column_config.DatetimeColumn("Date", format="DD/MM/YYYY"),
            "Pluvio_du_jour": st.column_config.NumberColumn("Pluie (mm)", format="%.1f"),
            "Cumul_du_mois": st.column_config.NumberColumn("Cumul mois (mm)", format="%.1f"),
            "Cumul_periode": st.column_config.NumberColumn("Cumul période (mm)", format="%.1f")
        }
    )