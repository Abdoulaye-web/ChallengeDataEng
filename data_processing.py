import json
import requests
import pandas as pd
from pymongo import MongoClient
import mysql.connector
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

# Fonction pour charger les données dans MySql
def charger_donnees_dans_mysql(nom_fichier_csv, table_name):
    """
    Charge les données d'un fichier CSV dans une table MySQL.
    
    Args:
        nom_fichier_csv (str): Le chemin du fichier CSV à charger.
        table_name (str): Le nom de la table MySQL dans laquelle insérer les données.
    """
    # Paramètres de connexion à la base MySQL
    user = 'admin'
    password = 'admin'
    host = '172.18.0.6'
    database = 'airflow'
    port = '3306'

    try:
        # Connexion à la base de données MySQL
        conn = mysql.connector.connect(
            user=user, password=password, host=host, database=database, port=port
        )
        cursor = conn.cursor()

        # Charger le fichier CSV en DataFrame
        df = pd.read_csv(nom_fichier_csv)
        if df.empty:
            print(f"Aucune donnée à insérer pour la table '{table_name}'.")
            return

        # Création de la table si elle n'existe pas
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                `date` DATE NOT NULL,
                `CO_moyen` FLOAT,
                `PM2.5_moyen` FLOAT
            );
        """)
        print(f"Table '{table_name}' créée ou déjà existante.")

        # Insertion des données dans la table
        for _, row in df.iterrows():
            cursor.execute(
                f"""
                INSERT INTO {table_name} (`date`, `CO_moyen`, `PM2.5_moyen`) 
                VALUES (%s, %s, %s)
                """,
                (row['date'], row['CO_moyen'], row['PM2.5_moyen'])
            )
        print(f"Données insérées dans la table MySQL '{table_name}'.")

        conn.commit()  # Confirmer l'insertion

    except mysql.connector.Error as e:
        print(f"Erreur de connexion ou d'insertion dans MySQL : {e}")
    
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
            print("Connexion à MySQL fermée.")


# Fonction principale
def main():
    # Station 1
    id_station1 = 283164601
    fichier_station1 = 'station1_data.json'
    chemin_json1 = extraire_et_stocker_donnees(id_station1, fichier_station1)
    chemin_csv1 = transformer_donnees(fichier_station1)
    if chemin_csv1:
        charger_donnees_dans_mongo(chemin_csv1, 'station1')
        charger_donnees_dans_mysql(chemin_csv1, 'station1')


    # Station 2
    id_station2 = 283181971
    fichier_station2 = 'station2_data.json'
    chemin_json2 = extraire_et_stocker_donnees(id_station2, fichier_station2)
    chemin_csv2 = transformer_donnees(fichier_station2)
    if chemin_csv2:
        charger_donnees_dans_mongo(chemin_csv2, 'station2')
        charger_donnees_dans_mysql(chemin_csv2, 'station2')
    
# Charger les données dans les tables `station1` et `station2`
    charger_donnees_dans_mysql('station1_data_Result.csv', 'station1')
    charger_donnees_dans_mysql('station2_data_Result.csv', 'station2')


if __name__ == "__main__":
    main()
