from airflow import DAG
from airflow.providers.amazon.aws.operators.glue import AwsGlueJobOperator
from airflow.providers.amazon.aws.sensors.glue import AwsGlueJobSensor
from airflow.utils.dates import days_ago

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
}

with DAG(
    dag_id='b_decision.tb_history_applicants',
    default_args=default_args,
    description='Responsável pelo trigger da b_decision.tb_history_applicants',
    schedule_interval='0 5 * * *',
    start_date=days_ago(1),
    catchup=False,
    tags=['glue', 'aws'],
) as dag:

    start_glue_job = AwsGlueJobOperator(
        task_id='start_glue_job',
        job_name='db_decision.tb_history_applicants',
        region_name='us-east-1',
        verbose=True
    )

    wait_for_glue_job = AwsGlueJobSensor(
        task_id='wait_for_glue_job_completion',
        job_name='db_decision.tb_history_applicants',
        run_id="{{ task_instance.xcom_pull(task_ids='start_glue_job')['JobRunId'] }}",
        region_name='us-east-1',
        poke_interval=60, 
        timeout=60 * 60,
    )

    start_glue_job >> wait_for_glue_job