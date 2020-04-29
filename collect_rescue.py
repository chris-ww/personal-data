import pandas as pd 
import sys
import os
sys.path.append('sites/tracker')
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
import sqlite3,time
from datetime import timedelta,datetime
from airflow.operators.python_operator import PythonOperator
from datetime import timedelta,datetime
from packages.importer import collect_rescue




default_args = {
    """
    airflow default arguments
    """
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(7),
    'email': ['ww.chris@outlook.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


dag = DAG(
    """
    airflow directed acyclic graph(dag)
    """
    'rescue_import',
    default_args=default_args,
    description='rescue import',
    schedule_interval='31 15 * * *',
)

collect_rescue = PythonOperator(
  """
  collects data from rescuetime api
  """
  task_id='Collect_rescue', 
  python_callable=collect_rescue, 
  provide_context=True,
  dag=dag
)

