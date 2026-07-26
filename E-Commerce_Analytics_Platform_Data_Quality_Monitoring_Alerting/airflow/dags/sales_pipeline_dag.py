from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.models import Variable
from airflow.exceptions import AirflowFailException
from datetime import datetime, timedelta
import requests
import logging

def send_telegram_alert(context):
    bot_token = Variable.get("TELEGRAM_BOT_TOKEN", default_var=None)
    chat_id = Variable.get("TELEGRAM_CHAT_ID", default_var=None)
    if bot_token and chat_id:
        msg = f"🚨 DAG {context['dag'].dag_id} failed: {context['exception']}"
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": msg})

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2026, 1, 1),
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'on_failure_callback': send_telegram_alert
}

def run_ge_validation(**kwargs):
    import sys
    sys.path.append('/opt/airflow/scripts')
    from run_ge_validation import run_ge_suite
    try:
        run_ge_suite("raw.orders", "orders_expectations")
    except Exception as e:
        raise AirflowFailException(f"GE failed: {e}")

def generate_profile():
    import sys
    sys.path.append('/opt/airflow/scripts')
    from profile_data import profile_data
    profile_data()

with DAG(
    'sales_pipeline',
    default_args=default_args,
    schedule_interval='0 8 * * *',
    catchup=False,
    max_active_runs=1,
    doc_md='''Расширенный пайплайн с мониторингом качества'''
) as dag:

    start = DummyOperator(task_id='start')

    generate_data = BashOperator(
        task_id='generate_data',
        bash_command='python /opt/airflow/scripts/generate_data.py',
        env={
            'DBT_USER': '{{ var.value.DBT_USER if var.value.DBT_USER else "analytics" }}',
            'DBT_PASSWORD': '{{ var.value.DBT_PASSWORD if var.value.DBT_PASSWORD else "analytics_pass" }}',
            'DBT_HOST': '{{ var.value.DBT_HOST if var.value.DBT_HOST else "postgres" }}',
            'DBT_PORT': '{{ var.value.DBT_PORT if var.value.DBT_PORT else "5432" }}',
            'DBT_DB': '{{ var.value.DBT_DB if var.value.DBT_DB else "analytics_db" }}'
        }
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /opt/airflow/dbt && dbt run --profiles-dir . && dbt snapshot --profiles-dir .',
        env={'DBT_PROFILES_DIR': '/opt/airflow/dbt'}
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/dbt && dbt test --profiles-dir .',
        env={'DBT_PROFILES_DIR': '/opt/airflow/dbt'}
    )

    ge_validation = PythonOperator(
        task_id='ge_validation',
        python_callable=run_ge_validation
    )

    profile_task = PythonOperator(
        task_id='profile_data',
        python_callable=generate_profile,
        trigger_rule='all_success'
    )

    dbt_docs = BashOperator(
        task_id='dbt_docs',
        bash_command='cd /opt/airflow/dbt && dbt docs generate --profiles-dir .',
        env={'DBT_PROFILES_DIR': '/opt/airflow/dbt'}
    )

    send_metrics = BashOperator(
        task_id='send_metrics',
        bash_command='echo "airflow.task.duration $(( $(date +%s) - {{ ts_nodash }} ))" | nc -u statsd-exporter 9125',
        trigger_rule='all_done'
    )

    start >> generate_data >> ge_validation >> dbt_run >> dbt_test >> [dbt_docs, profile_task, send_metrics]
