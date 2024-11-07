import os
import sys
from functools import lru_cache
from logging import getLogger

from airflow.listeners import hookimpl
from airflow.models.dagrun import DagRun
from airflow.plugins_manager import AirflowPlugin

from airflow_priority import AirflowPriorityConfigurationOptionNotFound, DagStatus, get_config_option, has_priority_tag

__all__ = ("get_client", "get_channel_id", "send_metric_slack", "on_dag_run_failed", "SlackPriorityPlugin")


_log = getLogger(__name__)


@lru_cache
def get_client():
    from slack_sdk import WebClient

    return WebClient(token=get_config_option("slack", "token"))


@lru_cache
def get_channel_id():
    channel_name = get_config_option("slack", "channel")
    conversations = get_client().conversations_list(types=["public_channel", "private_channel"])
    if conversations.data["ok"]:
        for channel in conversations.data["channels"]:
            if channel["name"] == channel_name:
                return channel["id"]
    raise Exception("TODO")


def send_metric_slack(dag_id: str, priority: int, tag: DagStatus) -> None:
    get_client().chat_postMessage(channel=get_channel_id(), text=f'A P{priority} DAG "{dag_id}" has {tag}!')


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
        send_metric_slack(dag_id, priority, "failed")


class SlackPriorityPlugin(AirflowPlugin):
    name = "SlackPriorityPlugin"
    listeners = []


try:
    if os.environ.get("SPHINX_BUILDING", "0") != "1":
        # Call once to ensure plugin will work
        import slack_sdk  # noqa: F401

        get_config_option("slack", "token")
        get_config_option("slack", "channel")
    SlackPriorityPlugin.listeners.append(sys.modules[__name__])
except (ImportError, AirflowPriorityConfigurationOptionNotFound):
    _log.warning("slack plugin could not be enabled! Ensure `slack-sdk` is installed and all configuration options are set.")
