import logging

import pandas as pd
import psycopg2
from airflow.decorators import dag, task, task_group
from airflow.models import Variable
from pendulum import datetime

SHOPS = Variable.get("orders_sync_shops", deserialize_json=True)
conn = psycopg2.connect(host="pg-eu.internal", dbname="shop", user="etl", password="etl-Secret-2024")
REGIONS = [row[0] for row in conn.cursor().execute("SELECT DISTINCT region FROM shops") or []]


@dag(
    dag_id="orders_sync",
    schedule="0 2 * * *",
    start_date=datetime(2026, 1, 1, tz="Europe/Paris"),
    catchup=False,
)
def orders_sync():
    @task
    def extract(shop):
        try:
            return pd.read_sql(f"SELECT * FROM orders WHERE shop = '{shop}'", conn)
        except Exception as error:
            logging.warning("extract failed for %s: %s", shop, error)
            return pd.DataFrame()

    @task
    def load(frame, table):
        logging.info("loading %s rows into %s", len(frame), table)

    @task_group
    def per_shop(shop):
        frame = extract(shop)
        load.partial(frame=frame).expand(table=["orders", "orders_archive"])

    per_shop.expand(shop=SHOPS)


orders_sync()
