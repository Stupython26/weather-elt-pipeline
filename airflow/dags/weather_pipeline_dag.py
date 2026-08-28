from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    "owner": "airflow",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weather_elt_pipeline",
    default_args=default_args,
    description="Extract weather data -> Load to Postgres -> Transform to star schema",
    schedule_interval="@hourly",
    start_date=datetime(2026, 1, 1),
    catchup=False,
    tags=["weather", "elt"],
    template_searchpath=["/opt/airflow/sql"],
) as dag:

    extract_task = BashOperator(
        task_id="extract_weather_data",
        bash_command="cd /opt/airflow/extractor && python extract_weather.py",
    )
    create_tables_task = PostgresOperator(
        task_id="create_mart_tables",
        postgres_conn_id="postgres_default",
        sql="create_mart_tables.sql",
    )

    transform_task = PostgresOperator(
        task_id="transform_weather_data",
        postgres_conn_id="postgres_default",
        sql="transform_weather.sql",
    )

    extract_task >> create_tables_task >> transform_task