import streamlit as st
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objs as go
import os

# Titre de l'application
st.title("Graphiques Financiers avec Indicateurs Techniques")

# -------------------------------
# Barre latérale pour les paramètres
# -------------------------------
st.sidebar.header("Paramètres de l'analyse")

# Sélection de l'actif
asset = st.sidebar.selectbox("Choisissez l'actif :", ("GOLD", "BTC", "S&P500"))

# Choix de la période d'analyse
start_date = st.sidebar.date_input("Date de début", datetime.date(2020, 1, 1))
end_date = st.sidebar.date_input("Date de fin", datetime.date.today())

# Sélection des indicateurs à afficher
afficher_SMA = st.sidebar.checkbox("Afficher SMA", value=True)
afficher_EMA = st.sidebar.checkbox("Afficher EMA", value=True)
afficher_MACD = st.sidebar.checkbox("Afficher MACD", value=True)
afficher_RSI = st.sidebar.checkbox("Afficher RSI", value=True)

# Choix de la période pour les moyennes mobiles
window_sma = st.sidebar.slider("Période SMA", min_value=5, max_value=100, value=20)
window_ema = st.sidebar.slider("Période EMA", min_value=5, max_value=100, value=20)

# Conversion explicite des dates en Timestamp
start_date = pd.to_datetime(start_date)
end_date = pd.to_datetime(end_date)

# -------------------------------
# Définir le nom du fichier CSV à charger selon l'actif
# -------------------------------
if asset == "GOLD":
    file_name = "XAU(GOLD).csv"
elif asset == "BTC":
    file_name = "BTC.csv"
elif asset == "S&P500":
    file_name = "S&P500.csv"

# Vérifier que le fichier existe
if not os.path.exists(file_name):
    st.error(f"Le fichier {file_name} n'existe pas.")
    st.stop()

# -------------------------------
# Chargement des données à partir du CSV
# -------------------------------
# On suppose que le CSV contient les colonnes : Date, Close, Open, High, Low
# La colonne Date est au format MM/DD/YYYY (exemple : 02/09/2025)
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

# Tri du DataFrame par date (important pour le slicing)
df.sort_index(inplace=True)

# -------------------------------
# Filtrage des données selon la plage de dates sélectionnée
# -------------------------------
df = df.loc[start_date: end_date]
if df.empty:
    st.error("Pas de données disponibles pour la période sélectionnée.\n" +
             "Vérifiez que la période sélectionnée inclut les dates présentes dans le fichier CSV.")
    st.stop()

# Le tableau de données n'est plus affiché pour aucun actif
# (Pour afficher les données, décommentez la ou les lignes suivantes)
# st.subheader(f"Données pour {asset}")
# st.write(df.head())

# -------------------------------
# Calcul des indicateurs techniques
# -------------------------------

# 1. Rendement journalier et rendement cumulé
df['Rendement'] = df['Close'].pct_change()
rendement_cumule = (df['Close'].iloc[-1] / df['Close'].iloc[0]) - 1

# 2. Volatilité annualisée (basée sur l'écart-type des rendements journaliers)
volatilite = df['Rendement'].std() * np.sqrt(252)

# 3. Sharpe Ratio (en supposant un taux sans risque nul)
sharpe_ratio = (df['Rendement'].mean() / df['Rendement'].std()) * np.sqrt(252)

# Affichage des indicateurs principaux dans la barre latérale
st.sidebar.markdown("### Indicateurs Globaux")
st.sidebar.write(f"**Rendement cumulé :** {rendement_cumule:.2%}")
st.sidebar.write(f"**Volatilité annualisée :** {volatilite:.2%}")
st.sidebar.write(f"**Sharpe Ratio :** {sharpe_ratio:.2f}")

# 4. Moyenne Mobile Simple (SMA)
df['SMA'] = df['Close'].rolling(window=window_sma).mean()

# 5. Moyenne Mobile Exponentielle (EMA)
df['EMA'] = df['Close'].ewm(span=window_ema, adjust=False).mean()

# 6. MACD (Moving Average Convergence Divergence)
ema_12 = df['Close'].ewm(span=12, adjust=False).mean()
ema_26 = df['Close'].ewm(span=26, adjust=False).mean()
df['MACD'] = ema_12 - ema_26
df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

# 7. RSI (Relative Strength Index) sur 14 jours
delta = df['Close'].diff()
up = delta.clip(lower=0)
down = -delta.clip(upper=0)
roll_up = up.rolling(window=14).mean()
roll_down = down.rolling(window=14).mean()
RS = roll_up / roll_down
df['RSI'] = 100.0 - (100.0 / (1.0 + RS))

# -------------------------------
# Graphique principal : Bougies (Candlestick) avec SMA et EMA
# -------------------------------
fig = go.Figure()

# Ajouter le graphique en bougies
fig.add_trace(go.Candlestick(x=df.index,
                             open=df['Open'],
                             high=df['High'],
                             low=df['Low'],
                             close=df['Close'],
                             name='Bougies'))

# Superposition des indicateurs SMA et EMA si sélectionnés
if afficher_SMA:
    fig.add_trace(go.Scatter(x=df.index, y=df['SMA'],
                             mode='lines',
                             name=f'SMA ({window_sma} jours)'))
if afficher_EMA:
    fig.add_trace(go.Scatter(x=df.index, y=df['EMA'],
                             mode='lines',
                             name=f'EMA ({window_ema} jours)'))

fig.update_layout(title=f"Évolution du {asset}",
                  xaxis_title="Date",
                  yaxis_title="Prix",
                  template="plotly_white")

st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Graphique MACD
# -------------------------------
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

# -------------------------------
# Graphique RSI
# -------------------------------
if afficher_RSI:
    fig_rsi = go.Figure()
    fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'],
                                 mode='lines',
                                 name='RSI'))
    # Lignes de seuil pour le RSI (30 et 70)
    fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
    fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
    fig_rsi.update_layout(title="RSI (Relative Strength Index)",
                          xaxis_title="Date",
                          yaxis_title="RSI",
                          yaxis=dict(range=[0, 100]),
                          template="plotly_white")
    st.plotly_chart(fig_rsi, use_container_width=True)
