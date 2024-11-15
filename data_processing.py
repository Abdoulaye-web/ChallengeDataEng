import json
import requests
import pandas as pd
from pymongo import MongoClient
import os

# Chemin de base
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Fonction pour extraire et stocker les données
def extraire_et_stocker_donnees(id_station, nom_fichier):
    chemin_complet = os.path.join(BASE_DIR, nom_fichier)
    url = f"https://airqino-api.magentalab.it/v3/getStationHourlyAvg/{id_station}"
    
    # Envoyer une requête HTTP GET
    reponse = requests.get(url)
    print(f"Téléchargement des données pour la station {id_station}...")

    # Charger les données JSON
    donnees = json.loads(reponse.text).get("data", [])
    print(f"Données reçues pour la station {id_station}: {len(donnees)} entrées")

    # Enregistrer les données dans un fichier JSON
    with open(chemin_complet, 'w') as f:
        json.dump(donnees, f)

    print(f"Données stockées dans le fichier : {chemin_complet}")
    return chemin_complet

# Fonction pour transformer les données
def transformer_donnees(nom_fichier):
    chemin_complet = os.path.join(BASE_DIR, nom_fichier)
    
    # Charger les données JSON
    with open(chemin_complet, 'r') as f:
        donnees = json.load(f)

    # Créer un DataFrame Pandas
    df = pd.DataFrame(donnees)
    if df.empty:
        print(f"Aucune donnée disponible dans {nom_fichier}.")
        return None

    # Transformer les données
    df['date'] = pd.to_datetime(df['timestamp']).dt.date
    colonnes_numeriques = df.select_dtypes(include='number').columns
    df_journalier = df.groupby('date')[colonnes_numeriques].mean()
    df_journalier['CO_moyen'] = df_journalier.get('CO', 0)
    df_journalier['PM2.5_moyen'] = df_journalier.get('PM2.5', 0)
    df_resultat = df_journalier[['CO_moyen', 'PM2.5_moyen']].reset_index()

    # Sauvegarder les données transformées en CSV
    fichier_csv = f"{nom_fichier}_Result.csv"
    chemin_csv = os.path.join(BASE_DIR, fichier_csv)
    df_resultat.to_csv(chemin_csv, index=False)
    print(f"Données transformées enregistrées dans : {chemin_csv}")

    return chemin_csv

# Fonction pour charger les données dans MongoDB
def charger_donnees_dans_mongo(nom_fichier_csv, nom_collection):
    uri_mongo = 'mongodb://mongoadmin:mongoadmin@172.26.128.1:27018/airflow?authSource=airflow'
    client_mongo = MongoClient(uri_mongo)
    db = client_mongo['airflow']
    collection = db[nom_collection]

    # Charger le fichier CSV en DataFrame
    df = pd.read_csv(nom_fichier_csv)
    if df.empty:
        print(f"Aucune donnée à insérer pour la collection {nom_collection}.")
        return

    # Insérer les données dans MongoDB
    donnees_json = json.loads(df.to_json(orient='records'))
    collection.insert_many(donnees_json)
    print(f"Données insérées dans la collection MongoDB '{nom_collection}'.")

# Fonction principale
def main():
    # Station 1
    id_station1 = 283164601
    fichier_station1 = 'station1_data.json'
    chemin_json1 = extraire_et_stocker_donnees(id_station1, fichier_station1)
    chemin_csv1 = transformer_donnees(fichier_station1)
    if chemin_csv1:
        charger_donnees_dans_mongo(chemin_csv1, 'station1')

    # Station 2
    id_station2 = 283181971
    fichier_station2 = 'station2_data.json'
    chemin_json2 = extraire_et_stocker_donnees(id_station2, fichier_station2)
    chemin_csv2 = transformer_donnees(fichier_station2)
    if chemin_csv2:
        charger_donnees_dans_mongo(chemin_csv2, 'station2')

if __name__ == "__main__":
    main()
