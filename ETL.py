from data_processing import extraire_et_stocker_donnees, transformer_donnees, charger_donnees_dans_mongo

from data_processing import extraire_et_stocker_donnees, transformer_donnees, charger_donnees_dans_mongo

def main():
    # Spécifier les ID de station et les noms de fichier pour chaque station
    id_station1 = 283164601
    fichier_station1 = 'station1_data.json'
    id_station2 = 283181971
    fichier_station2 = 'station2_data.json'

    # Extraire et stocker les données pour la première station
    extraire_et_stocker_donnees(id_station1, fichier_station1)

    # Extraire et stocker les données pour la deuxième station
    extraire_et_stocker_donnees(id_station2, fichier_station2)

    # Transformer les données pour chaque station
    df_station1 = transformer_donnees(fichier_station1)
    df_station2 = transformer_donnees(fichier_station2)

    # Charger les données dans MongoDB pour chaque station
    charger_donnees_dans_mongo(df_station1, 'station1')
    charger_donnees_dans_mongo(df_station2, 'station2')

if __name__ == "__main__":
    main()
