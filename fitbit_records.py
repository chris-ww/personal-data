import pandas as pd 
import datetime
import sys
import os
sys.path.append('sites/tracker')
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.utils.dates import days_ago
import sqlite3,time
from datetime import timedelta,datetime
from airflow.operators.python_operator import PythonOperator

from packages.importer import collect_sleep,collect_fitbit_day,collect_food,collect_activity,collect_body,fitbit_client,collect_calendar,collect_location, create_connection, select_all_tasks




default_args = {
    """
    airflow default arguments
    """
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': days_ago(117),
    'email': ['ww.chris@outlook.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}


dag = DAG(
    """
    airflow dag
    """
    'import',
    default_args=default_args,
    description='Daily import',
    schedule_interval='30 15 * * *',
)

collect_fitbit = PythonOperator(
  """
  collects data from fitbit api
  """
  task_id='Connect_fitbit', 
  python_callable=collect_fitbit_day, 
  provide_context=True,
  dag=dag
)

