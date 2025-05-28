import streamlit as st
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.stats import norm
import plotly.graph_objects as go


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
    /* [Votre CSS existant reste inchangé] */
    
    /* Ajouts spécifiques pour la prédiction */
    .prediction-card {{
        background: linear-gradient(135deg, rgba(0,180,216,0.1), rgba(67,170,139,0.1));
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        border-left: 4px solid {COLORS['vivid_orange']};
        transition: all 0.3s ease;
    }}
    
    .prediction-metric {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {COLORS['dark_blue']};
        margin-bottom: 5px;
    }}
    
    .prediction-value {{
        font-size: 1.8rem;
        font-weight: 700;
        margin: 10px 0;
    }}
    
    .alert-badge {{
        background-color: {COLORS['raspberry_pink']};
        color: white;
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-left: 10px;
    }}
</style>
""", unsafe_allow_html=True)

# --- Classe de prédiction ---
class RainfallPredictor:
    def __init__(self, look_back=12, forecast_horizon=6):
        self.look_back = look_back
        self.forecast_horizon = forecast_horizon
        self.scaler = MinMaxScaler()
        
    def prepare_data(self, data):
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1)).flatten()
        
        if len(scaled_data) <= self.look_back + self.forecast_horizon:
            raise ValueError("Données insuffisantes pour la prédiction")
        
        X, y = [], []
        for i in range(len(scaled_data) - self.look_back - self.forecast_horizon + 1):
            X.append(scaled_data[i:i+self.look_back])
            y.append(scaled_data[i+self.look_back:i+self.look_back+self.forecast_horizon])
        
        return np.array(X), np.array(y)
    
    def build_model(self):
        model = keras.Sequential([
            layers.LSTM(64, activation='relu', input_shape=(self.look_back, 1), return_sequences=True),
            layers.Dropout(0.2),
            layers.LSTM(32, activation='relu'),
            layers.Dense(self.forecast_horizon)
        ])
        model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001),
                    loss='mse')
        return model
    
    def train_predict(self, data):
        try:
            X, y = self.prepare_data(data)
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            model = self.build_model()
            
            early_stopping = keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
            
            history = model.fit(
                X_train, y_train,
                epochs=100,
                batch_size=32,
                validation_split=0.2,
                callbacks=[early_stopping],
                verbose=0
            )
            
            predictions = model.predict(X_test)
            y_test_orig = self.scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
            predictions_orig = self.scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()
            
            mse = mean_squared_error(y_test_orig, predictions_orig)
            mae = mean_absolute_error(y_test_orig, predictions_orig)
            
            return predictions_orig, mse, mae, history
        except Exception as e:
            st.error(f"Erreur lors de la prédiction: {str(e)}")
            return None, None, None, None

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
            Analyse et prédiction des précipitations
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🔍 Filtres")
    selected_year = st.slider("Année", 1982, 2018, (2000, 2010))
    show_map = st.checkbox("Afficher la carte", value=True)
    show_stats = st.checkbox("Afficher les statistiques", value=True)
    
    st.markdown("---")
    st.markdown("### 🔮 Paramètres de Prédiction")
    forecast_months = st.slider("Mois à prédire", 1, 12, 6)
    look_back = st.slider("Historique (mois)", 6, 36, 12)
    alert_threshold = st.slider("Seuil d'alerte (mm)", 0.0, 100.0, 30.0)

# --- En-tête Principal ---
st.markdown(f"""
<div style="background: white; padding: 25px; border-radius: 12px; margin-bottom: 30px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
    <h1 style="color: {COLORS['dark_blue']}; margin: 0; text-align: center; font-weight: 700;">
        🌧️ SmartSDGTunisia - Analyse et Prédiction Pluviométrique
    </h1>
    <p style="color: {COLORS['dark_blue']}90; text-align: center; margin: 10px 0 0 0; font-size: 16px;">
        Données historiques et prévisions des précipitations par station météorologique
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
            
            m = folium.Map(location=[merged_df['Lat'].mean(), merged_df['Long'].mean()], zoom_start=7)
            
            for idx, row in merged_df.iterrows():
                folium.CircleMarker(
                    location=[row['Lat'], row['Long']],
                    radius=row['Valeur']/10,
                    popup=f"{row['Station']}<br>Moyenne: {row['Valeur']:.1f} mm",
                    color=COLORS['sky_blue'],
                    fill=True,
                    fill_color=COLORS['sky_blue']
                ).add_to(m)
            
            st_folium(m, width="100%", height=500)
    
    with col_stats:
        if show_stats:
            st.markdown("""
            <div class="local-kpi-container">
                <div class="local-kpi-title">📊 STATISTIQUES PAR STATION</div>
            """, unsafe_allow_html=True)
            
            selected_station = st.selectbox(
                "Choisir une station",
                options=merged_df['Station'].unique(),
                index=0
            )
            
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
            
            rank = int(merged_df['Valeur'].rank(ascending=False, method='min').loc[merged_df['Station'] == selected_station].values[0])
            
            st.markdown(f"""
            <div class="local-kpi-card" style="text-align:center; background: rgba(26,26,46,0.03);">
                <div style="font-size:0.9rem; color:#555;">Classement National</div>
                <div style="display:inline-block; margin:0 15px;">
                    <div style="font-size:0.8rem;">Précipitations</div>
                    <div style="font-size:1.5rem; font-weight:700; color:{COLORS['dark_blue']}">#{rank}</div>
                </div>
            </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"<h2 class='section-title'>📋 Données Complètes</h2>", unsafe_allow_html=True)
            st.dataframe(station_data.to_frame().T, 
                        hide_index=True,
                        use_container_width=True)

# --- Visualisation des données temporelles ---
st.markdown(f"<h2 class='section-title'>📈 Évolution Temporelle</h2>", unsafe_allow_html=True)

selected_stations = st.multiselect(
    "Sélectionnez les stations à visualiser",
    options=merged_df['Station'].unique(),
    default=merged_df.nlargest(3, 'Valeur')['Station'].tolist()
)

if selected_stations:
    station_ids = merged_df[merged_df['Station'].isin(selected_stations)]['ID'].tolist()
    available_columns = [col for col in df.columns if col != 'Date']
    valid_station_ids = [str(id) for id in station_ids if str(id) in available_columns]
    
    if not valid_station_ids:
        st.warning("Aucune donnée disponible pour les stations sélectionnées.")
    else:
        df_filtered = df[['Date'] + valid_station_ids]
        df_filtered = df_filtered.melt(id_vars='Date', var_name='ID', value_name='Précipitation')
        df_filtered['ID'] = df_filtered['ID'].astype(int)
        df_filtered = pd.merge(df_filtered, merged_df[['ID', 'Station']], on='ID')
        
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
        
        # --- Section Prédiction ---
        st.markdown(f"<h2 class='section-title'>🔮 Prévisions des Précipitations</h2>", unsafe_allow_html=True)
        
        station_to_predict = st.selectbox(
            "Station à analyser",
            options=selected_stations,
            index=0
        )
        
        station_id = merged_df[merged_df['Station'] == station_to_predict]['ID'].values[0]
        rainfall_data = df[str(station_id)].dropna().values
        
        if len(rainfall_data) < look_back + forecast_months:
            st.warning(f"Données insuffisantes pour {station_to_predict}. Nécessite au moins {look_back + forecast_months} mois de données.")
        else:
            predictor = RainfallPredictor(look_back, forecast_months)
            
            with st.spinner("Calcul des prévisions en cours..."):
                predictions, mse, mae, history = predictor.train_predict(rainfall_data)
            
            if predictions is not None:
                # Création des dates de prédiction
                last_date = pd.to_datetime(df['Date'].iloc[-1])
                forecast_dates = pd.date_range(
                    start=last_date,
                    periods=forecast_months+1,
                    freq='M'
                )[1:]
                
                # KPI de prédiction
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"""
                    <div class="prediction-card">
                        <div class="prediction-metric">Précision du modèle (MSE)</div>
                        <div class="prediction-value" style="color:{COLORS['sky_blue']}">{mse:.2f}</div>
                        <div>Plus la valeur est basse, meilleure est la prédiction</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="prediction-card">
                        <div class="prediction-metric">Erreur moyenne (MAE)</div>
                        <div class="prediction-value" style="color:{COLORS['mint_green']}">{mae:.2f} mm</div>
                        <div>Écart moyen entre prévisions et réalité</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Graphique de prédiction
                fig_pred = go.Figure()
                
                # Données historiques
                fig_pred.add_trace(go.Scatter(
                    x=df['Date'],
                    y=df[str(station_id)],
                    name='Données Historiques',
                    line=dict(color=COLORS['sky_blue'], width=2),
                    hovertemplate='%{y:.1f} mm<extra></extra>'
                ))
                
                # Prédictions
                fig_pred.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=predictions[-forecast_months:],
                    name='Prévisions',
                    line=dict(color=COLORS['vivid_orange'], width=2, dash='dot'),
                    hovertemplate='%{y:.1f} mm<extra></extra>'
                ))
                
                # Seuil d'alerte
                fig_pred.add_hline(
                    y=alert_threshold,
                    line_dash="dash",
                    line_color=COLORS['raspberry_pink'],
                    annotation_text=f"Seuil d'alerte: {alert_threshold}mm",
                    annotation_position="bottom right"
                )
                
                # Zones d'alerte
                above_threshold = [y if y > alert_threshold else None for y in predictions[-forecast_months:]]
                if any(above_threshold):
                    fig_pred.add_trace(go.Scatter(
                        x=forecast_dates,
                        y=above_threshold,
                        mode='markers',
                        marker=dict(color=COLORS['raspberry_pink'], size=10),
                        name='Dépassement de seuil',
                        hovertemplate='%{y:.1f} mm<extra></extra>'
                    ))
                
                # Mise en forme
                fig_pred.update_layout(
                    title=f"Prévisions pour {station_to_predict}",
                    xaxis_title="Date",
                    yaxis_title="Précipitation (mm)",
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    hovermode='x unified',
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                st.plotly_chart(fig_pred, use_container_width=True)
                
                # Détection des alertes
                alert_months = []
                for i, pred in enumerate(predictions[-forecast_months:]):
                    if pred > alert_threshold:
                        alert_months.append({
                            "Mois": forecast_dates[i].strftime("%B %Y"),
                            "Précipitation prévue": f"{pred:.1f} mm",
                            "Dépassement": f"{pred - alert_threshold:.1f} mm"
                        })
                
                if alert_months:
                    st.markdown(f"""
                    <div style="background-color: rgba(241,91,181,0.1); border-left: 4px solid {COLORS['raspberry_pink']}; 
                                padding: 15px; border-radius: 8px; margin-bottom: 20px;">
                        <h3 style="color: {COLORS['raspberry_pink']}; margin-top: 0;">
                            ⚠️ Alertes de précipitations intenses
                        </h3>
                        <p>Les mois suivants dépassent le seuil d'alerte de {alert_threshold} mm :</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    alert_df = pd.DataFrame(alert_months)
                    st.dataframe(
                        alert_df.style.applymap(
                            lambda x: f"color: {COLORS['raspberry_pink']}; font-weight: bold",
                            subset=["Dépassement"]
                        ),
                        hide_index=True,
                        use_container_width=True
                    )
                else:
                    st.success(f"Aucun dépassement du seuil d'alerte prévu pour les {forecast_months} prochains mois.")
else:
    st.warning("Veuillez sélectionner au moins une station pour visualiser les données temporelles.")