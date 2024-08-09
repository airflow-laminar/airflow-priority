import os
import sys
from functools import lru_cache
from logging import getLogger

from airflow.listeners import hookimpl
from airflow.models.dagrun import DagRun
from airflow.plugins_manager import AirflowPlugin
from newrelic_telemetry_sdk import GaugeMetric, MetricClient

from airflow_priority import AirflowPriorityConfigurationOptionNotFound, DagStatus, get_config_option, has_priority_tag

__all__ = (
    "send_metric_newrelic",
    "on_dag_run_running",
    "on_dag_run_success",
    "on_dag_run_failed",
    "NewRelicPriorityPlugin",
)

_log = getLogger(__name__)


@lru_cache
def get_client():
    return MetricClient(get_config_option("newrelic", "api_key"))


def send_metric_newrelic(dag_id: str, priority: int, tag: DagStatus) -> None:
    priority = GaugeMetric(
        f"airflow.custom.priority.p{priority}.{tag}", 1, tags={"application": "airflow", "dag": dag_id, "priority": priority, "tag": tag}
    )
    get_client().send_batch([priority])


@hookimpl
def on_dag_run_running(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_newrelic(dag_id, priority, "running")


@hookimpl
def on_dag_run_success(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_newrelic(dag_id, priority, "success")


@hookimpl
def on_dag_run_failed(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_newrelic(dag_id, priority, "failed")


try:
    if os.environ.get("SPHINX_BUILDING", "0") != "1":
        # Call once to ensure plugin will work
        get_config_option("newrelic", "api_key")

    class NewRelicPriorityPlugin(AirflowPlugin):
        name = "NewRelicPriorityPlugin"
        listeners = [sys.modules[__name__]]
except AirflowPriorityConfigurationOptionNotFound:
    _log.exception("Plugin could not be enabled")
