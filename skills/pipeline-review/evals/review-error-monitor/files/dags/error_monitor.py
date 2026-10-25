"""Report new replication errors to the chat room every hour."""

import json

import requests
from airflow.decorators import dag, task
from airflow.hooks.base import BaseHook
from airflow.models import Variable
from pendulum import datetime, now

STATE = "error_monitor_state"


@dag(
    dag_id="error_monitor",
    schedule="@hourly",
    start_date=datetime(2026, 1, 1, tz="UTC"),
    catchup=False,
    default_args={"retries": 3},
)
def error_monitor():
    @task
    def read_errors():
        state = json.loads(Variable.get(STATE, default_var='{"last_run": "2026-01-01T00:00:00+00:00"}'))
        api = BaseHook.get_connection("replication_api")
        response = requests.post(
            f"{api.host}/api/v1/mirrors/logs",
            json={"level": "error", "since": state["last_run"]},
            auth=(api.login, api.password),
            timeout=30,
        )
        Variable.set(STATE, json.dumps({"last_run": now("UTC").isoformat()}))
        return response.json()["errors"]

    @task
    def summarize(errors):
        llm = BaseHook.get_connection("llm")
        reply = requests.post(
            f"{llm.host}/v1/chat/completions",
            json={"messages": [{"role": "user", "content": "Summarize: " + json.dumps(errors)}]},
            timeout=300,
        )
        reply.raise_for_status()
        return reply.json()["choices"][0]["message"]["content"]

    @task
    def send(errors, summary):
        webhook = BaseHook.get_connection("chat_webhook").host
        for error in errors:
            requests.post(webhook, json={"text": f"{error['flowName']}: {error['errorMessage']}"}, timeout=10)
        requests.post(webhook, json={"text": summary}, timeout=10)

    errors = read_errors()
    send(errors, summarize(errors))


error_monitor()
