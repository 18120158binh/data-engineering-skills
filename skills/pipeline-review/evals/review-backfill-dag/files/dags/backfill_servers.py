"""Copy the history of every source server into the warehouse."""

import requests
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from pendulum import datetime, now

INVENTORY = "replicated_servers"


@dag(
    dag_id="backfill_servers",
    schedule="@daily",
    start_date=datetime(2026, 1, 1, tz="Africa/Johannesburg"),
    catchup=False,
    default_args={"retries": 3},
)
def backfill_servers():
    @task
    def list_servers():
        api = BaseHook.get_connection("discovery_api")
        try:
            response = requests.get(f"{api.host}/servers", timeout=30)
            return response.json().get("servers", [])
        except requests.RequestException:
            return []

    @task
    def plan_copies(servers):
        Variable.set(INVENTORY, ",".join(s["name"] for s in servers))
        today = now()
        months = [today.subtract(months=n).format("YYYYMM") for n in range(1, 13)]
        return [{"server": s["name"], "month": m} for s in servers for m in months]

    @task(execution_timeout=None)
    def remove_missing(servers):
        known = set(Variable.get(INVENTORY, default_var="").split(","))
        current = {s["name"] for s in servers}
        replication = BaseHook.get_connection("replication_api")
        for name in known - current:
            requests.post(f"{replication.host}/api/v1/mirrors/drop", json={"name": name}, timeout=30)

    @task(retries=5)
    def copy_month(item):
        replication = BaseHook.get_connection("replication_api")
        response = requests.post(
            f"{replication.host}/api/v1/mirrors/copy",
            json={"source": item["server"], "partition": item["month"]},
            timeout=600,
        )
        response.raise_for_status()

    servers = list_servers()
    remove_missing(servers)
    copy_month.expand(item=plan_copies(servers))


backfill_servers()
