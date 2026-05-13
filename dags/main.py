from airflow import DAG
import pendulum 
from datetime import datetime, timedelta
from Api.video_stats import getPlaylistId, getVideoResult, video_data
from datawarehouse.dw import staging_table, core_table
from data_quality.soda import yt_elt_dq

local_tz= pendulum.timezone("Asia/Kuala_Lumpur")

default_args= {
    'owner': 'Thiyane Xavier',
    'depends_on_past':False,
    'email_on_failure': False,
    'email_on_retry': False,
    'email': 'thiyane97@gmail.com',
    # 'retries': 1,
    # 'retry_delay' : timedelta(minutes=5),
    'max_active_runs': 1,
    'dagrun_timeout':1,
    'start_date':datetime(2025,1,1,tzinfo=local_tz),
    'end_date': datetime(2030,12,31,tzinfo=local_tz),
}

with DAG(
    dag_id= 'final_json',
    default_args=default_args,
    description = 'DAG para produzir json com dados brutos',
    schedule = '0 13 * * *',
    catchup=False
) as dag:

    # Define Tasks
    playlist_id = getPlaylistId()
    video_ids = getVideoResult(playlist_id)
    extracted_data = video_data(video_ids)

    # Define dependencies
    playlist_id >> video_ids >> extracted_data
    
with DAG(
    dag_id= 'updated_db',
    default_args=default_args,
    description = 'DAG para passar os dados transformados para a base de dados',
    schedule = '0 14 * * *',
    catchup=False
) as dag:

    # Define Tasks
    updated_staging = staging_table()
    updated_core = core_table()

    # Define dependencies
    updated_staging >> updated_core

#variables
staging_schema = "staging"
core_schema = "core"
with DAG(
    dag_id= 'data_quality_check',
    default_args=default_args,
    description = 'DAG para verificar a qualidade dos dados na base de dados',
    schedule = '0 15 * * *',
    catchup=False
) as dag:

    # Define Tasks
    soda_check_staging = yt_elt_dq(staging_schema)
    soda_check_core = yt_elt_dq(core_schema)

    # Define dependencies
    soda_check_staging >> soda_check_core 