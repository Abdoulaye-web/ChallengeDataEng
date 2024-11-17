# ChallengeDataEng
1-Extraire les données depuis l'API Airquino
2-Calcul le CO et le PM2.5 par jour de chaque capteur
3-Stocker les resultats dans une base de donnée MongoDB
4-Fournir un Dashboard superset pour visualiser les données 

### Le projet a pour objectif de développer un ETL (Extract, Transform, Load) permettant l'extraction et le traitement des données relatives à la qualité de l'air en provenance de l'API AirQuino. Par la suite, des graphiques seront créés pour fournir des visualisations des données à intervalles d'une heure.

### STRUCTURE DU PROJET : 

**docker-compose.yml**:
Ce fichier définit les services nécessaires à l'exécution du projet dans un environnement Docker. Il contient des services pour :

**Postgres** : Base de données pour Airflow.
**MongoDB** : Base de données NoSQL utilisée pour stocker les données traitées.
**Airflow** : Plusieurs services pour exécuter Apache Airflow (Scheduler, Webserver, Init).
**Superset** : Pour la visualisation des données.
**Redis et MySQL** : Pour d'autres services liés à Airflow et à la gestion des flux de travail.
Il inclut également des volumes pour persister les données et des réseaux pour connecter les services.



**data_processing.py** :
Ce script effectue les étapes suivantes :

Extraire les données : Il envoie une requête GET à une API pour extraire des données spécifiques sur des stations (via des IDs de station).
Transformer les données : Après avoir récupéré les données au format JSON, le script les convertit en un DataFrame Pandas, applique des transformations pour calculer des moyennes journalières, et organise les colonnes de manière spécifique.
Charger dans MongoDB : Les données transformées sont ensuite converties en format JSON et insérées dans une base de données MongoDB.



## La fonction main() automatise les étapes nécessaires pour :

Collecter,
Transformer
Stocker,
Charger les données des stations dans une base de données MongoDB.


**DAG Airflow (dags/)** :

Tâches définies :
1. Extraction des données :
extract_station1 : Extrait les données de la station 283164601 et les enregistre dans station1_data.json.
extract_station2 : Extrait les données de la station 283181971 et les enregistre dans station2_data.json.
2. Transformation des données :
transform_station1 : Transforme les données de station1_data.json en calculant les moyennes journalières, puis enregistre les résultats dans station1_data.json_Result.csv.
transform_station2 : Transforme les données de station2_data.json en calculant les moyennes journalières, puis enregistre les résultats dans station2_data.json_Result.csv.
3. Chargement des données dans MongoDB :
load_station1 : Charge les données transformées (station1_data.json_Result.csv) dans la collection MongoDB station1.
load_station2 : Charge les données transformées (station2_data.json_Result.csv) dans la collection MongoDB station2.

**Superset Viz**: 
L'intégration de Superset dans ce projet permet de rendre les données traitées via l'ETL accessibles et compréhensibles grâce à des visualisations dynamiques et interactives. Ces visualisations sont essentielles pour donner du sens aux données collectées, permettant aux utilisateurs de prendre des décisions éclairées basées sur les tendances observées dans les stations de mesure.


### REPONSES AUX QUESTIONS 

**1. Quelle serait votre stratégie de mise en production de votre ETL?**

La stratégie de mise en production de notre système ETL repose sur plusieurs étapes clés. Tout d'abord, nous garantirons sa stabilité en réalisant des tests approfondis dans un environnement de pré-production. Ces tests automatisés et d'évaluation des performances permettront de valider le bon fonctionnement du système avant son déploiement en production.

Les mises à jour et correctifs seront gérés de manière fluide grâce à des outils de gestion de versions comme Git. Le déploiement contrôlé sera assuré par Ansible, tandis que des procédures de retour à la version précédente seront mises en place pour pallier tout problème éventuel.

Afin de gérer l'augmentation prévue de la charge, nous utiliserons Kubernetes, qui permettra d'ajuster dynamiquement la capacité du système en fonction des besoins.


**2- Quelle serait votre stratégie pour que declencher votre ETL automatiquement chaque heure ?**

La stratégie pour déclencher automatiquement notre système ETL chaque heure repose sur l'utilisation d'Apache Airflow, qui sera configuré pour exécuter le pipeline ETL à intervalles réguliers. Un DAG (Directed Acyclic Graph) sera défini pour orchestrer l'exécution des tâches, incluant l'extraction, la transformation et le chargement des données.

Airflow sera configuré pour déclencher automatiquement l'exécution du pipeline à chaque heure, en utilisant la planification basée sur des cron expressions. Cela permettra de garantir une exécution fiable et synchronisée à l'heure prévue, sans intervention manuelle.

De plus, pour assurer la robustesse du système, des alertes et des notifications seront mises en place pour signaler toute erreur ou échec dans l'exécution du pipeline ETL. En cas de défaillance, des mécanismes de reprise seront activés pour redémarrer le processus de manière autonome et garantir la continuité des opérations.
