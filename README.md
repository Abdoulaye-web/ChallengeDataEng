# ChallengeDataEng
Mettre en place un ETL pour visualisation

1-Extraire les données depuis l'API Airquino
2-Calcul le CO et le PM2.5 par jour de chaque capteur
3-Stocker les resultats dans une base de donnée MongoDB
4-Fournir un Dashboard superset pour visualiser les données 

Le projet vise à construire un ETL (Extract, Transform, Load) pour l'extraction et le traitement des données relatives à la qualité de l'air provenant de l'API AirQuino. Ensuite il s'agira de la création d'un modèle de Machine Learning pour effectuer des prévisions sur les deux prochaines heures.

STRUCTURE DU PROJET : 

** docker-compose.yml :
Ce fichier définit les services nécessaires à l'exécution du projet dans un environnement Docker. Il contient des services pour :

Postgres : Base de données pour Airflow.
MongoDB : Base de données NoSQL utilisée pour stocker les données traitées.
Airflow : Plusieurs services pour exécuter Apache Airflow (Scheduler, Webserver, Init).
Superset : Pour la visualisation des données.
Redis et MySQL : Pour d'autres services liés à Airflow et à la gestion des flux de travail.
Il inclut également des volumes pour persister les données et des réseaux pour connecter les services.



**data_processing.py :
Ce script effectue les étapes suivantes :

Extraire les données : Il envoie une requête GET à une API pour extraire des données spécifiques sur des stations (via des IDs de station).
Transformer les données : Après avoir récupéré les données au format JSON, le script les convertit en un DataFrame Pandas, applique des transformations pour calculer des moyennes journalières, et organise les colonnes de manière spécifique.
Charger dans MongoDB : Les données transformées sont ensuite converties en format JSON et insérées dans une base de données MongoDB.



**etl.py :
Ce script utilise les fonctions définies dans data_processing.py pour exécuter le pipeline ETL. Il traite deux stations de données en les extrayant, les transformant et en les chargeant dans MongoDB


**DAG Airflow (dags/) :
Le fichier DAG définit un flux de travail dans Apache Airflow pour exécuter les scripts ETL et de traitement des données :

Tâche ETL : Exécute le script etl.py.
Tâche de traitement des données : Exécute le script data_processing.py.
Les deux tâches sont définies dans un DAG avec une séquence d'exécution (la tâche ETL s'exécute avant la tâche de traitement des données).
Airflow est utilisé pour orchestrer et automatiser le processus d'extraction, de transformation, et de chargement des données.

**Superset Viz: 
L'intégration de Superset dans ce projet permet de rendre les données traitées via l'ETL accessibles et compréhensibles grâce à des visualisations dynamiques et interactives. Ces visualisations sont essentielles pour donner du sens aux données collectées, permettant aux utilisateurs de prendre des décisions éclairées basées sur les tendances observées dans les stations de mesure.


REPONSES AUX QUESTIONS 

1. Quelle serait votre stratégie de mise en production de votre ETL?

La stratégie de mise en production de notre système ETL repose sur plusieurs étapes clés. Tout d'abord, nous garantirons sa stabilité en réalisant des tests approfondis dans un environnement de pré-production. Ces tests automatisés et d'évaluation des performances permettront de valider le bon fonctionnement du système avant son déploiement en production.

Les mises à jour et correctifs seront gérés de manière fluide grâce à des outils de gestion de versions comme Git. Le déploiement contrôlé sera assuré par Ansible, tandis que des procédures de retour à la version précédente seront mises en place pour pallier tout problème éventuel.

Afin de gérer l'augmentation prévue de la charge, nous utiliserons Kubernetes, qui permettra d'ajuster dynamiquement la capacité du système en fonction des besoins.


2- Quelle serait votre stratégie pour que declencher votre ETL automatiquement chaque heure ?

La stratégie pour déclencher automatiquement notre système ETL chaque heure repose sur l'utilisation d'Apache Airflow, qui sera configuré pour exécuter le pipeline ETL à intervalles réguliers. Un DAG (Directed Acyclic Graph) sera défini pour orchestrer l'exécution des tâches, incluant l'extraction, la transformation et le chargement des données.

Airflow sera configuré pour déclencher automatiquement l'exécution du pipeline à chaque heure, en utilisant la planification basée sur des cron expressions. Cela permettra de garantir une exécution fiable et synchronisée à l'heure prévue, sans intervention manuelle.

De plus, pour assurer la robustesse du système, des alertes et des notifications seront mises en place pour signaler toute erreur ou échec dans l'exécution du pipeline ETL. En cas de défaillance, des mécanismes de reprise seront activés pour redémarrer le processus de manière autonome et garantir la continuité des opérations.
