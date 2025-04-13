import streamlit as st
import plotly.express as px
from scripts.arabic_utils import normalize_arabic

def show_dashboard(properties, df, graph_type):
    if not properties or df is None:
        st.info("Cliquez sur une délégation pour afficher les données")
        return
    
    del_ar = properties.get('del_ar')
    del_fr = properties.get('del_fr', 'Inconnu')
    
    st.markdown(f"### 📊 Données pour: {del_fr} / {del_ar}")
    
    normalized_del = normalize_arabic(del_ar)
    matching_stations = [
        station for station in df['station'].unique()
        if normalize_arabic(station) == normalized_del
    ]
    
    if not matching_stations:
        st.warning(f"Aucune station ne correspond à {del_ar}")
        return
    
    station_data = df[df['station'].isin(matching_stations)]
    
    if station_data.empty:
        st.warning("Données pluviométriques non disponibles")
        return
    
    latest = station_data.iloc[-1]
    cols = st.columns(3)
    cols[0].metric("Pluie du jour", f"{latest['Pluvio_du_jour']} mm")
    cols[1].metric("Cumul mensuel", f"{latest['Cumul_du_mois']} mm")
    cols[2].metric("Cumul période", f"{latest['Cumul_periode']} mm")
    
    if graph_type == "Courbe":
        fig = px.line(station_data, x='Date', y='Pluvio_du_jour', 
                    title=f"Pluviométrie à {del_fr}")
    elif graph_type == "Barres":
        fig = px.bar(station_data, x='Date', y='Pluvio_du_jour', 
                    title=f"Pluviométrie à {del_fr}")

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(station_data.sort_values('Date', ascending=False))
