from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from data_processing import extraire_et_stocker_donnees, transformer_donnees, charger_donnees_dans_mongo
from data_processing import charger_donnees_dans_mysql

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=2),
}

with DAG(
    'data_etl_pipeline',
    default_args=default_args,
    description='DAG for extracting, transforming, and loading data into MongoDB',
    schedule_interval='30 23 * * *',  # Exécution quotidienne à 23h30
    start_date=datetime(2023, 11, 1, 23, 30),  # Date et heure de début
    catchup=False,
) as dag:

    def extract_and_store_task(id_station, nom_fichier):
        return extraire_et_stocker_donnees(id_station=id_station, nom_fichier=nom_fichier)

    def transform_task(nom_fichier):
        return transformer_donnees(nom_fichier=nom_fichier)

    def load_to_mongo_task(nom_collection):
        charger_donnees_dans_mongo(nom_fichier_csv="/opt/airflow/dags/station1_data.json_Result.csv", nom_collection=nom_collection)
        charger_donnees_dans_mongo(nom_fichier_csv="/opt/airflow/dags/station2_data.json_Result.csv", nom_collection=nom_collection)

    # Ajout d'une nouvelle tâche de chargement dans MySQL pour chaque station
    def load_to_mysql_task(nom_fichier_csv, table_name):
        charger_donnees_dans_mysql(nom_fichier_csv, table_name)

    # Extraction tasks for each station
    extract_station1 = PythonOperator(
        task_id='extract_station1',
        python_callable=extract_and_store_task,
        op_kwargs={'id_station': 283164601, 'nom_fichier': 'station1_data.json'}
    )

    extract_station2 = PythonOperator(
        task_id='extract_station2',
        python_callable=extract_and_store_task,
        op_kwargs={'id_station': 283181971, 'nom_fichier': 'station2_data.json'}
    )

    # Transformation tasks for each station
    transform_station1 = PythonOperator(
        task_id='transform_station1',
        python_callable=transform_task,
        op_kwargs={'nom_fichier': 'station1_data.json'}
    )

    transform_station2 = PythonOperator(
        task_id='transform_station2',
        python_callable=transform_task,
        op_kwargs={'nom_fichier': 'station2_data.json'}
    )

    # Loading tasks for each station
    load_station1 = PythonOperator(
        task_id='load_station1_to_mongo',
        python_callable=load_to_mongo_task,
        op_kwargs={'nom_collection': 'station1'}
    )

    load_station2 = PythonOperator(
        task_id='load_station2_to_mongo',
        python_callable=load_to_mongo_task,
        op_kwargs={'nom_collection': 'station2'}
    )

    # Tâches de chargement dans MySQL pour chaque station
    load_station1_mysql = PythonOperator(
        task_id='load_station1_to_mysql',
        python_callable=load_to_mysql_task,
        op_kwargs={'nom_fichier_csv': '/opt/airflow/dags/station1_data.json_Result.csv', 'table_name': 'station1'}
    )

    load_station2_mysql = PythonOperator(
        task_id='load_station2_to_mysql',
        python_callable=load_to_mysql_task,
        op_kwargs={'nom_fichier_csv': '/opt/airflow/dags/station2_data.json_Result.csv', 'table_name': 'station2'}   
    )
    # Define the task dependencies
    extract_station1 >> transform_station1 >> load_station1 >> load_station1_mysql
    extract_station2 >> transform_station2 >> load_station2 >> load_station2_mysql
