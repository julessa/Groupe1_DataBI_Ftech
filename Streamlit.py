import streamlit as st
st.set_page_config(layout="wide")  # Affichage en mode full-width

# ======================================================
# Pop-up de conditions légales
# ======================================================
if 'accepted' not in st.session_state:
    st.markdown("""
        <style>
            .main * {
                filter: blur(5px);
                pointer-events: none;
                user-select: none;
            }
            button {
                background: #4CAF50 !important;
                color: white !important;
                border: none;
                padding: 10px 25px;
                border-radius: 5px;
                margin-top: 15px;
            }
        </style>
    """, unsafe_allow_html=True)

    with st.container():

        
        st.markdown("<h3>⚠️ Avertissement Légal - Risques d'Investissement</h3>", unsafe_allow_html=True)
        st.markdown("""
            <p>Les transactions sur instruments financiers comportent un <strong>niveau élevé de risque</strong> et peuvent ne pas convenir à tous les investisseurs.</p>
            <p>Il est possible de subir des pertes supérieures à votre investissement initial.</p>
            <p>Les performances passées ne préjugent pas des résultats futurs.</p>
            <p>En cliquant sur "Accepter", vous reconnaissez avoir pris connaissance de ces risques.</p>
        """, unsafe_allow_html=True)
        
        # Bouton centré, apparaissant sous le contenu de la pop-up
        if st.button("Accepter les conditions d'utilisation"):
            st.session_state.accepted = True
            st.rerun()
        
        # Fermer la div de la pop-up
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()  # Bloque l'exécution du reste de l'application


import pandas as pd
import numpy as np
import datetime
import plotly.graph_objs as go
import os

# Pour la partie prédictions
from prophet import Prophet
import matplotlib.pyplot as plt
import plotly.express as px

st.title("Analyse Financière : Analyse, Comparaison et Prédictions")

# Sélection du mode d'analyse via la barre latérale
mode = st.sidebar.radio("Mode d'analyse", ("Analyse Individuelle", "Comparaison", "Prédictions"))

# Sélection commune de la période pour tous les modes
start_date = st.sidebar.date_input("Date de début", datetime.date(2020, 1, 1))
end_date   = st.sidebar.date_input("Date de fin", datetime.date.today())
start_date = pd.to_datetime(start_date)
end_date   = pd.to_datetime(end_date)

# Dictionnaire associant chaque actif à son fichier CSV
asset_files = {
    "GOLD": "./CSV/df_gold.csv",
    "BTC": "./CSV/df_btc.csv",
    "S&P500": "./CSV/df_sp500.csv"
}

# ======================================================
# Mode 1 : Analyse Individuelle
# ======================================================
if mode == "Analyse Individuelle":
    asset = st.sidebar.selectbox("Choisissez l'actif :", list(asset_files.keys()))
    
    # Sélection des indicateurs techniques
    afficher_SMA = st.sidebar.checkbox("Afficher SMA", value=True)
    afficher_EMA = st.sidebar.checkbox("Afficher EMA", value=True)
    afficher_MACD = st.sidebar.checkbox("Afficher MACD", value=True)
    afficher_RSI = st.sidebar.checkbox("Afficher RSI", value=True)
    afficher_BB = st.sidebar.checkbox("Afficher Bollinger Bands", value=True)
    
    window_sma = st.sidebar.slider("Période SMA", min_value=5, max_value=100, value=20)
    window_ema = st.sidebar.slider("Période EMA", min_value=5, max_value=100, value=20)
    
    if afficher_BB:
        window_bb = st.sidebar.slider("Période BB", min_value=5, max_value=100, value=20)
        multiplier_bb = st.sidebar.number_input("Multiplicateur BB", min_value=1.0, max_value=5.0, value=2.0, step=0.1)
    
    file_name = asset_files[asset]
    if not os.path.exists(file_name):
        st.error(f"Le fichier {file_name} n'existe pas.")
        st.stop()
        
    try:
        df = pd.read_csv(
            file_name,
            parse_dates=['Date'],
            date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d'),
            index_col='Date'
        )
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier {file_name}: {e}")
        st.stop()
        
    if df.empty:
        st.error("Le DataFrame est vide après le chargement du fichier.")
        st.stop()
        
    df.sort_index(inplace=True)
    df = df.loc[start_date: end_date]
    if df.empty:
        st.error("Pas de données disponibles pour la période sélectionnée.")
        st.stop()
        
    # Calcul des indicateurs techniques pour affichage individuel
    df['Rendement'] = df['Close'].pct_change()
    rendement_cumule = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1
    volatilite = df['Rendement'].std() * np.sqrt(252)
    sharpe_ratio = (df['Rendement'].mean() / df['Rendement'].std()) * np.sqrt(252)
    
    st.sidebar.markdown("### Indicateurs Globaux")
    st.sidebar.write(f"**Rendement cumulé :** {rendement_cumule:.2%}")
    st.sidebar.write(f"**Volatilité annualisée :** {volatilite:.2%}")
    st.sidebar.write(f"**Sharpe Ratio :** {sharpe_ratio:.2f}")
    
    # Moyennes mobiles et autres indicateurs
    df['SMA'] = df['Close'].rolling(window=window_sma).mean()
    df['EMA'] = df['Close'].ewm(span=window_ema, adjust=False).mean()
    
    ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
    ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = ema_12 - ema_26
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
    
    delta = df['Close'].diff()
    up = delta.clip(lower=0)
    down = -delta.clip(upper=0)
    roll_up = up.rolling(window=14).mean()
    roll_down = down.rolling(window=14).mean()
    RS = roll_up / roll_down
    df['RSI'] = 100.0 - (100.0 / (1.0 + RS))
    
    # Calcul des Bollinger Bands si sélectionné
    if afficher_BB:
        df['BB_MA'] = df['Close'].rolling(window=window_bb).mean()
        df['BB_std'] = df['Close'].rolling(window=window_bb).std()
        df['BB_upper'] = df['BB_MA'] + (multiplier_bb * df['BB_std'])
        df['BB_lower'] = df['BB_MA'] - (multiplier_bb * df['BB_std'])
    
    # Graphique en bougies avec indicateurs
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close'],
        name='Bougies'
    ))
    if afficher_SMA:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['SMA'],
            mode='lines',
            name=f'SMA ({window_sma} jours)'
        ))
    if afficher_EMA:
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['EMA'],
            mode='lines',
            name=f'EMA ({window_ema} jours)'
        ))
    if afficher_BB:
        # Trace pour la bande supérieure (invisible)
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['BB_upper'],
            mode='lines',
            line=dict(color='rgba(128, 0, 128, 0)'),
            showlegend=False,
            hoverinfo='skip'
        ))
        # Trace pour la bande inférieure avec zone remplie entre BB_upper et BB_lower
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['BB_lower'],
            mode='lines',
            fill='tonexty',
            fillcolor='rgba(128, 0, 128, 0.2)',  # couleur violet avec 20% d'opacité
            line=dict(color='rgba(128, 0, 128, 0)'),
            name='Bollinger Bands',
            hoverinfo='skip'
        ))
        # Trace pour la moyenne des Bollinger Bands
        fig.add_trace(go.Scatter(
            x=df.index,
            y=df['BB_MA'],
            mode='lines',
            name='BB MA',
            line=dict(color='orange')
        ))
    
    fig.update_layout(title=f"Évolution de {asset}",
                      xaxis_title="Date",
                      yaxis_title="Prix",
                      template="plotly_white",
                      height=600)
    st.plotly_chart(fig, use_container_width=True)
    
    # Graphique MACD
    if afficher_MACD:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(
            x=df.index,
            y=df['MACD'],
            mode='lines',
            name='MACD'
        ))
        fig_macd.add_trace(go.Scatter(
            x=df.index,
            y=df['Signal_Line'],
            mode='lines',
            name='Signal Line'
        ))
        fig_macd.update_layout(title="MACD",
                               xaxis_title="Date",
                               yaxis_title="Valeur",
                               template="plotly_white",
                               height=400)
        st.plotly_chart(fig_macd, use_container_width=True)
    
    # Graphique RSI
    if afficher_RSI:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(
            x=df.index,
            y=df['RSI'],
            mode='lines',
            name='RSI'
        ))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(title="RSI (Relative Strength Index)",
                              xaxis_title="Date",
                              yaxis_title="RSI",
                              yaxis=dict(range=[0, 100]),
                              template="plotly_white",
                              height=400)
        st.plotly_chart(fig_rsi, use_container_width=True)

# ======================================================
# Mode 2 : Comparaison
# ======================================================
elif mode == "Comparaison":
    assets = st.sidebar.multiselect(
        "Sélectionnez les actifs à comparer",
        list(asset_files.keys()),
        default=list(asset_files.keys())
    )
    if not assets:
        st.error("Veuillez sélectionner au moins un actif pour la comparaison.")
        st.stop()
        
    normalized_data = {}
    metrics_data = {}  # Dictionnaire pour stocker les indicateurs de performance
    # Pour chaque actif sélectionné, on calcule la série normalisée et les indicateurs
    for a in assets:
        file_name = asset_files[a]
        if not os.path.exists(file_name):
            st.error(f"Le fichier {file_name} n'existe pas pour {a}.")
            continue
        try:
            df_asset = pd.read_csv(
                file_name,
                parse_dates=['Date'],
                date_parser=lambda x: pd.to_datetime(x, format='%Y-%m-%d'),
                index_col='Date'
            )
        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier {file_name} pour {a}: {e}")
            continue
        if df_asset.empty:
            st.error(f"Le DataFrame pour {a} est vide après le chargement du fichier.")
            continue
        df_asset.sort_index(inplace=True)
        df_asset = df_asset.loc[start_date: end_date]
        if df_asset.empty:
            st.error(f"Pas de données disponibles pour {a} dans la période sélectionnée.")
            continue
        
        # Série normalisée (première valeur ramenée à 100)
        norm_series = df_asset['Close'] / df_asset['Close'].iloc[0] * 100
        normalized_data[a] = norm_series
        
        # Calcul des indicateurs de performance
        returns = df_asset['Close'].pct_change()
        volatility = returns.std() * np.sqrt(252) * 100  # en %
        sharpe = (returns.mean() / returns.std()) * np.sqrt(252) if returns.std() != 0 else np.nan
        # Calcul du RSI moyen sur une fenêtre de 14 jours
        delta = df_asset['Close'].diff()
        up = delta.clip(lower=0)
        down = -delta.clip(upper=0)
        roll_up = up.rolling(window=14).mean()
        roll_down = down.rolling(window=14).mean()
        RSI = 100.0 - (100.0 / (1.0 + roll_up / roll_down))
        avg_RSI = RSI.mean()
        # Rendement annualisé (%) calculé à partir du ratio final/premier, annualisé sur la durée du DataFrame
        n = len(df_asset)
        if n > 1:
            annual_return = ((df_asset['Close'].iloc[-1] / df_asset['Close'].iloc[0]) ** (252 / n) - 1) * 100
        else:
            annual_return = np.nan
        
        metrics_data[a] = {
            "Volatilité": round(volatility, 2),
            "Ratio de Sharpe": round(sharpe, 2),
            "RSI moyen": round(avg_RSI, 2),
            "Rendement annualisé": round(annual_return, 2)
        }
        
    if not normalized_data:
        st.error("Aucune donnée disponible pour les actifs sélectionnés dans la période spécifiée.")
        st.stop()
        
    # Combinaison des séries normalisées (intersection des dates)
    compare_df = pd.concat(normalized_data, axis=1, join='inner')
    
    # Graphique comparatif agrandi
    fig_compare = go.Figure()
    for asset_name in compare_df.columns:
        fig_compare.add_trace(go.Scatter(
            x=compare_df.index,
            y=compare_df[asset_name],
            mode='lines',
            name=asset_name
        ))
    fig_compare.update_layout(title="Comparaison des performances normalisées",
                              xaxis_title="Date",
                              yaxis_title="Performance (indexé à 100)",
                              template="plotly_white",
                              height=600)
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # Création du tableau comparatif des indicateurs de performance
    desired_order = ["BTC", "GOLD", "S&P500"]
    final_order = [a for a in desired_order if a in metrics_data]
    indicators = ["Volatilité", "Ratio de Sharpe", "RSI moyen", "Rendement annualisé"]
    table_data = {"Indicateur": indicators}
    for a in final_order:
        table_data[a] = [f"{metrics_data[a][ind]}%" if ind == "Rendement annualisé" else metrics_data[a][ind] for ind in indicators]
    metrics_df = pd.DataFrame(table_data)
    
    st.subheader("Comparaison des indicateurs de performance")
    st.markdown(metrics_df.to_html(index=False), unsafe_allow_html=True)

# ======================================================
# Mode 3 : Prédictions
# ======================================================
elif mode == "Prédictions":
    st.header("Prédictions des prix - Modèle Prophet")
    
    def load_and_plot(asset_name, historical_path, forecast_path, perf_path):
        try:
            # Chargement des données
            df_hist = pd.read_csv(historical_path, parse_dates=['Date'])
            df_hist.rename(columns={'Date': 'ds', 'Close': 'y'}, inplace=True)
            
            forecast = pd.read_csv(forecast_path, parse_dates=['ds'])
            performance = pd.read_csv(perf_path)
            
            # Création du graphique
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_hist['ds'],
                y=df_hist['y'],
                name='Historique',
                line=dict(color='#1f77b4')
            ))
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['yhat'],
                name='Prévision',
                line=dict(color='#ff7f0e')
            ))
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['yhat_upper'],
                fill=None,
                line=dict(color='rgba(255,127,14,0.1)'),
                name='Intervalle de confiance'
            ))
            fig.add_trace(go.Scatter(
                x=forecast['ds'],
                y=forecast['yhat_lower'],
                fill='tonexty',
                line=dict(color='rgba(255,127,14,0.1)'),
                showlegend=False
            ))
            
            fig.update_layout(
                title=f"Prévision du prix - {asset_name}",
                xaxis_title="Date",
                yaxis_title="Prix",
                hovermode="x unified"
            )
            
            # Affichage du graphique
            st.plotly_chart(fig, use_container_width=True)
            
            # Calcul du score
            horizon_180 = performance[performance['horizon'] == '180 days']
            if not horizon_180.empty:
                rmse = horizon_180['rmse'].values[0]
                st.metric(label="Performance du modèle (RMSE sur 180 jours)", value=f"{rmse:.2f}")
            else:
                st.warning("Données de performance indisponibles pour cet horizon")

        except Exception as e:
            st.error(f"Erreur de chargement pour {asset_name} : {str(e)}")

    # Bitcoin
    st.subheader("Bitcoin")
    load_and_plot(
        "Bitcoin",
        "./CSV/df_btc.csv",
        "./CSV/prediction/forecast_btc.csv",
        "./CSV/prediction/performance_btc.csv"
    )

    # S&P 500
    st.subheader("S&P 500")
    load_and_plot(
        "S&P 500",
        "./CSV/df_sp500.csv", 
        "./CSV/prediction/forecast_sp500.csv",
        "./CSV/prediction/performance_sp500.csv"
    )

    # Or
    st.subheader("Or")
    load_and_plot(
        "Or",
        "./CSV/df_gold.csv",
        "./CSV/prediction/forecast_gold.csv",
        "./CSV/prediction/performance_gold.csv"
    )
