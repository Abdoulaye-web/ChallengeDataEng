import json
import requests
import pandas as pd
from pymongo import MongoClient

def extraire_et_stocker_donnees(id_station, nom_fichier):
    # URL de l'API avec l'ID de la station spécifique
    url = f"https://airqino-api.magentalab.it/v3/getStationHourlyAvg/{id_station}"

    # Envoyer une requête HTTP GET à l'URL et sauvegarder la réponse
    reponse = requests.get(url)

    # Charger les données JSON à partir de la réponse
    print("fichier en cours de déléchargement.............................................|||")
    donnees = json.loads(reponse.text)
    donnees = donnees["data"]

    # Sauvegarder les données dans un fichier JSON
    print("Écriture dans le fichier JSON..................................................|||")
    with open(nom_fichier, 'w') as f:
        json.dump(donnees, f)

def transformer_donnees(nom_fichier):
    # Charger les données JSON à partir du fichier
    with open(nom_fichier, 'r') as f:
        donnees = json.load(f)

    # Créer un DataFrame à partir des données
    df = pd.DataFrame(donnees)

    # Convertir la colonne 'timestamp' en type datetime
    df['date'] = pd.to_datetime(df['timestamp']).dt.date

    # Sélectionner uniquement les colonnes numériques pour le calcul de la moyenne
    colonnes_numeriques = df.select_dtypes(include='number').columns
    df_journalier = df.groupby('date')[colonnes_numeriques].mean()

    # Ajouter des colonnes pour les moyennes CO et PM2.5
    df_journalier['CO_moyen'] = df_journalier['CO']
    df_journalier['PM2.5_moyen'] = df_journalier['PM2.5']

    # Ajouter la colonne 'date' au DataFrame final
    df_journalier['date'] = pd.to_datetime(df_journalier.index)

    # Reorganiser les colonnes pour avoir 'date' en premier
    resultat_df = df_journalier[['date', 'CO_moyen', 'PM2.5_moyen']]

    return resultat_df

def charger_donnees_dans_mongo(df, nom_collection, nom_base_donnees='airflow', uri_mongo='mongodb://localhost:27017'):
    # Connexion à MongoDB
    client_mongo = MongoClient(uri_mongo, 
                               username='admin', 
                               password='admin@', 
                               authSource='admin')

    # Sélection de la base de données
    db = client_mongo[nom_base_donnees]

    # Sélection de la collection
    collection = db[nom_collection]

    # Ajouter la colonne 'date' dans les données
    df['date'] = df.index.astype(str)

    # Convertir le DataFrame en un dictionnaire JSON
    donnees_json = json.loads(df.to_json(orient='records'))

    # Insérer les données dans la collection MongoDB
    collection.insert_many(donnees_json)



 
