import pandas as pd

# Chemins des fichiers
btc_file = "CSV/BTC.csv"
sp500_file = "CSV/S&P500_filtered.csv"
gold_file = "CSV/XAU(GOLD)_filtered.csv"

# Fonction pour calculer la moyenne de clôture d'un fichier CSV
def calculer_moyenne(fichier, nom_actif):
    df = pd.read_csv(fichier)
    df.rename(columns={"Close/Last": "Close"}, inplace=True)  # Standardisation du nom de colonne
    moyenne = df["Close"].mean()
    print(f"Moyenne du prix de clôture pour {nom_actif} : {moyenne:.2f}")

# Calcul des moyennes pour chaque actif
calculer_moyenne(btc_file, "Bitcoin (BTC)")
calculer_moyenne(sp500_file, "S&P 500")
calculer_moyenne(gold_file, "Or (XAU)")
