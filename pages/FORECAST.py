import streamlit as st
import pandas as pd
import plotly.express as px
try:
    from statsmodels.tsa.seasonal import seasonal_decompose
except ImportError:
    st.error("Le module 'statsmodels' n'est pas installé. Veuillez exécuter: pip install statsmodels")
    st.stop()
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import numpy as np
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, mean_absolute_percentage_error
from scipy.stats import norm
import datetime
import folium
from streamlit_folium import folium_static

class TimeSeriesPredictor:
    def __init__(self, data, look_back=12, forecast_horizon=6):
        self.data = data
        self.look_back = look_back
        self.forecast_horizon = forecast_horizon
        self.scaler = MinMaxScaler()
        self.scaled_data = self.scaler.fit_transform(data.reshape(-1, 1)).flatten()

    def prepare_data(self):
        if len(self.scaled_data) <= self.look_back + self.forecast_horizon:
            raise ValueError("Données insuffisantes. Augmentez la taille des données ou réduisez look_back/forecast_horizon.")
        
        X, y = [], []
        for i in range(len(self.scaled_data) - self.look_back - self.forecast_horizon + 1):
            X.append(self.scaled_data[i:i+self.look_back])
            y.append(self.scaled_data[i+self.look_back:i+self.look_back+self.forecast_horizon])
        
        return np.array(X), np.array(y)

    def lstm_model(self):
        model = keras.Sequential([
            layers.LSTM(64, activation='relu', input_shape=(self.look_back, 1), return_sequences=True),
            layers.Dropout(0.2),
            layers.LSTM(32, activation='relu'),
            layers.Dense(self.forecast_horizon)
        ])
        model.compile(optimizer=keras.optimizers.Adam(learning_rate=0.001), 
                     loss='mse')
        return model

    def train_and_predict(self, model):
        try:
            X, y = self.prepare_data()
            X = X.reshape((X.shape[0], X.shape[1], 1))
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            early_stopping = keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=10,
                restore_best_weights=True
            )
            
            history = model.fit(X_train, y_train, 
                              epochs=100, 
                              batch_size=32,
                              validation_split=0.2, 
                              callbacks=[early_stopping], 
                              verbose=0)
            
            predictions = model.predict(X_test)
            
            y_test_orig = self.scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()
            predictions_orig = self.scaler.inverse_transform(predictions.reshape(-1, 1)).flatten()
            
            metrics = {
                'R²': r2_score(y_test_orig, predictions_orig),
                'RMSE': np.sqrt(mean_squared_error(y_test_orig, predictions_orig)),
                'MAE': mean_absolute_error(y_test_orig, predictions_orig),
                'MAPE': mean_absolute_percentage_error(y_test_orig, predictions_orig)
            }
            
            return predictions_orig, metrics, history
        except Exception as e:
            st.error(f"Erreur de prédiction: {str(e)}")
            return None, None, None

# Configuration de la page
st.set_page_config(
    page_title="🌧️ Prévision des Précipitations",
    layout="wide",
    page_icon="💧"
)

# Titre principal
st.title("🌧️ Prévision Avancée des Précipitations")

# Style CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Configuration")
    selected_model = st.selectbox("Modèle", ["LSTM"])
    forecast_horizon = st.slider("Horizon de prévision (mois)", 1, 12, 6)
    look_back = st.slider("Historique (mois)", 6, 36, 12)
    threshold_value = st.slider("Seuil de précipitations (mm)", 0.0, 100.0, 30.0)

# Upload de fichier
uploaded_file = st.file_uploader("Téléverser un fichier CSV", type="csv")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # Prétraitement
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.sort_values('Date')
    
    # Sélection de la station
    stations = df['Name'].unique()
    selected_station = st.selectbox("Sélectionner une station", stations)
    station_data = df[df['Name'] == selected_station]
    
    # Onglets
    tab1, tab2 = st.tabs(["📊 Analyse", "📈 Prévision"])
    
    with tab1:
        st.subheader(f"Analyse pour {selected_station}")
        
        # Graphique temporel
        fig = px.line(station_data, x='Date', y='Rainfall', 
                     title="Précipitations au fil du temps")
        st.plotly_chart(fig, use_container_width=True)
        
        # Décomposition saisonnière
        st.subheader("Décomposition Saisonnière")
        try:
            result = seasonal_decompose(station_data.set_index('Date')['Rainfall'], 
                                      model='additive', period=12)
            fig, axes = plt.subplots(4, 1, figsize=(12, 8))
            result.observed.plot(ax=axes[0])
            result.trend.plot(ax=axes[1])
            result.seasonal.plot(ax=axes[2])
            result.resid.plot(ax=axes[3])
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Impossible de décomposer: {e}")
    
    with tab2:
        st.subheader("Prévision des Précipitations")
        
        # Préparation des données
        input_data = station_data['Rainfall'].values
        
        if len(input_data) < look_back + forecast_horizon:
            st.error(f"Données insuffisantes. Nécessite au moins {look_back + forecast_horizon} mois.")
        else:
            predictor = TimeSeriesPredictor(input_data, look_back, forecast_horizon)
            model = predictor.lstm_model()
            
            with st.spinner("Entraînement du modèle en cours..."):
                prediction, metrics, history = predictor.train_and_predict(model)
            
            if prediction is not None:
                # Affichage des résultats
                cols = st.columns(4)
                cols[0].metric("Précision (R²)", f"{metrics['R²']:.2f}")
                cols[1].metric("Erreur Moyenne", f"{metrics['MAE']:.2f} mm")
                
                # Visualisation
                forecast_dates = pd.date_range(
                    start=station_data['Date'].iloc[-1],
                    periods=forecast_horizon+1,
                    freq='M'
                )[1:]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=station_data['Date'],
                    y=station_data['Rainfall'],
                    name='Historique'
                ))
                fig.add_trace(go.Scatter(
                    x=forecast_dates,
                    y=prediction[-forecast_horizon:],
                    name='Prévision',
                    line=dict(color='red')
                ))
                fig.update_layout(title="Prévision des Précipitations")
                st.plotly_chart(fig, use_container_width=True)
                
                # Alertes fortes précipitations
                heavy_rain = prediction > threshold_value
                if any(heavy_rain):
                    st.warning(f"⚠️ Fortes précipitations prévues sur {sum(heavy_rain)} mois")
else:
    st.info("Veuillez téléverser un fichier CSV pour commencer.")