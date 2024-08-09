import os
import sys
from asyncio import sleep
from functools import lru_cache
from logging import getLogger
from queue import Queue
from threading import Thread
from time import sleep as time_sleep

from airflow.listeners import hookimpl
from airflow.models.dagrun import DagRun
from airflow.plugins_manager import AirflowPlugin
from discord import Client, Intents

from airflow_priority import AirflowPriorityConfigurationOptionNotFound, DagStatus, get_config_option, has_priority_tag

__all__ = ("get_client", "send_metric_discord", "on_dag_run_failed", "DiscordPriorityPlugin")

_log = getLogger(__name__)


@lru_cache
def get_client():
    client = Client(intents=Intents.default())
    client.queue = Queue()

    @client.event
    async def on_ready():
        channel = client.get_channel(int(get_config_option("discord", "channel")))
        while True:
            while client.queue.empty():
                await sleep(5)
            await channel.send(client.queue.get())

    token = get_config_option("discord", "token")
    t = Thread(target=client.run, args=(token,), daemon=True)
    t.start()
    return client


def send_metric_discord(dag_id: str, priority: int, tag: DagStatus) -> None:
    client_queue = get_client().queue
    client_queue.put(f'A P{priority} DAG "{dag_id}" has {tag}!')
    while not client_queue.empty():
        time_sleep(1)


# @hookimpl
# def on_dag_run_running(dag_run: DagRun, msg: str):
#     dag_id, priority = has_priority_tag(dag_run=dag_run)
#     if priority:
#         send_metric_slack(dag_id, priority, "running")


# @hookimpl
# def on_dag_run_success(dag_run: DagRun, msg: str):
#     dag_id, priority = has_priority_tag(dag_run=dag_run)
#     if priority:
#         send_metric_slack(dag_id, priority, "succeeded")


@hookimpl
def on_dag_run_failed(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_discord(dag_id, priority, "failed")


try:
    if os.environ.get("SPHINX_BUILDING", "0") != "1":
        # Call once to ensure plugin will work
        get_config_option("discord", "channel")
        get_config_option("discord", "token")

    class DiscordPriorityPlugin(AirflowPlugin):
        name = "DiscordPriorityPlugin"
        listeners = [sys.modules[__name__]]
except AirflowPriorityConfigurationOptionNotFound:
    _log.exception("Plugin could not be enabled")
