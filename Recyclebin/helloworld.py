import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objs as go
import os

st.title("Analyse Financière : Analyse Individuelle et Comparaison des Actifs")

# ======================================================
# Paramètres communs et sélection du mode d'analyse
# ======================================================
# Choix du mode via un sélecteur radio
mode = st.sidebar.radio("Mode d'analyse", ("Analyse Individuelle", "Comparaison"))

# Sélection de la période d'analyse (commune aux deux modes)
start_date = st.sidebar.date_input("Date de début", datetime.date(2020, 1, 1))
end_date = st.sidebar.date_input("Date de fin", datetime.date.today())

# Conversion des dates en Timestamp (pour compatibilité)
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# Dictionnaire associant le nom de l'actif au fichier CSV correspondant
asset_files = {
    "GOLD": "XAU(GOLD).csv",
    "BTC": "BTC.csv",
    "S&P500": "S&P500.csv"
}

# ======================================================
# Mode 1 : Analyse Individuelle (graphique en bougies + indicateurs)
# ======================================================
if mode == "Analyse Individuelle":
    # Sélection de l'actif (uniquement un actif)
    asset = st.sidebar.selectbox("Choisissez l'actif :", list(asset_files.keys()))
    
    # Sélection des indicateurs techniques
    afficher_SMA = st.sidebar.checkbox("Afficher SMA", value=True)
    afficher_EMA = st.sidebar.checkbox("Afficher EMA", value=True)
    afficher_MACD = st.sidebar.checkbox("Afficher MACD", value=True)
    afficher_RSI = st.sidebar.checkbox("Afficher RSI", value=True)
    window_sma = st.sidebar.slider("Période SMA", min_value=5, max_value=100, value=20)
    window_ema = st.sidebar.slider("Période EMA", min_value=5, max_value=100, value=20)
    
    file_name = asset_files[asset]
    if not os.path.exists(file_name):
        st.error(f"Le fichier {file_name} n'existe pas.")
        st.stop()
        
    try:
        df = pd.read_csv(
            file_name,
            parse_dates=['Date'],
            date_parser=lambda x: pd.to_datetime(x, format='%m/%d/%Y'),
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
        
    # (Le tableau de données n'est pas affiché)
    
    # Calcul des indicateurs techniques
    df['Rendement'] = df['Close'].pct_change()
    rendement_cumule = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1
    volatilite = df['Rendement'].std() * np.sqrt(252)
    sharpe_ratio = (df['Rendement'].mean() / df['Rendement'].std()) * np.sqrt(252)
    
    st.sidebar.markdown("### Indicateurs Globaux")
    st.sidebar.write(f"**Rendement cumulé :** {rendement_cumule:.2%}")
    st.sidebar.write(f"**Volatilité annualisée :** {volatilite:.2%}")
    st.sidebar.write(f"**Sharpe Ratio :** {sharpe_ratio:.2f}")
    
    # Calcul des moyennes mobiles et autres indicateurs
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
    
    # Graphique en bougies avec indicateurs SMA et EMA superposés
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
        fig.add_trace(go.Scatter(x=df.index, y=df['SMA'],
                                 mode='lines',
                                 name=f'SMA ({window_sma} jours)'))
    if afficher_EMA:
        fig.add_trace(go.Scatter(x=df.index, y=df['EMA'],
                                 mode='lines',
                                 name=f'EMA ({window_ema} jours)'))
    fig.update_layout(title=f"Évolution de {asset}",
                      xaxis_title="Date",
                      yaxis_title="Prix",
                      template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    
    # Graphique MACD
    if afficher_MACD:
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'],
                                      mode='lines',
                                      name='MACD'))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'],
                                      mode='lines',
                                      name='Signal Line'))
        fig_macd.update_layout(title="MACD",
                               xaxis_title="Date",
                               yaxis_title="Valeur",
                               template="plotly_white")
        st.plotly_chart(fig_macd, use_container_width=True)
    
    # Graphique RSI
    if afficher_RSI:
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'],
                                     mode='lines',
                                     name='RSI'))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(title="RSI (Relative Strength Index)",
                              xaxis_title="Date",
                              yaxis_title="RSI",
                              yaxis=dict(range=[0, 100]),
                              template="plotly_white")
        st.plotly_chart(fig_rsi, use_container_width=True)
        
# ======================================================
# Mode 2 : Comparaison (graphique comparatif de performance normalisée)
# ======================================================
elif mode == "Comparaison":
    # Sélection multi-actifs
    assets = st.sidebar.multiselect(
        "Sélectionnez les actifs à comparer",
        list(asset_files.keys()),
        default=list(asset_files.keys())
    )
    if not assets:
        st.error("Veuillez sélectionner au moins un actif pour la comparaison.")
        st.stop()
        
    # Dictionnaire pour stocker les séries normalisées
    normalized_data = {}
    for a in assets:
        file_name = asset_files[a]
        if not os.path.exists(file_name):
            st.error(f"Le fichier {file_name} n'existe pas pour {a}.")
            continue
        try:
            df_asset = pd.read_csv(
                file_name,
                parse_dates=['Date'],
                date_parser=lambda x: pd.to_datetime(x, format='%m/%d/%Y'),
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
        
        # Normalisation de la série de prix de clôture
        # (la première valeur est ramenée à 100)
        norm_series = df_asset['Close'] / df_asset['Close'].iloc[0] * 100
        normalized_data[a] = norm_series
        
    if not normalized_data:
        st.error("Aucune donnée disponible pour les actifs sélectionnés dans la période spécifiée.")
        st.stop()
        
    # Combinaison des séries normalisées dans un DataFrame commun (intersection des dates)
    compare_df = pd.concat(normalized_data, axis=1, join='inner')
    
    # Graphique comparatif
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
                              template="plotly_white")
    st.plotly_chart(fig_compare, use_container_width=True)