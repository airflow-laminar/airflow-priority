import os
import sys
from datetime import datetime
from functools import lru_cache
from logging import getLogger

from airflow.listeners import hookimpl
from airflow.models.dagrun import DagRun
from airflow.plugins_manager import AirflowPlugin

from airflow_priority import AirflowPriorityConfigurationOptionNotFound, DagStatus, get_config_option, has_priority_tag

_log = getLogger(__name__)


@lru_cache
def get_client():
    from boto3 import client as Boto3Client
    from botocore.config import Config

    config = Config(region_name=get_config_option("aws", "region"), retries=dict(max_attempts=10, mode="adaptive"))
    return Boto3Client("cloudwatch", config=config)


def send_metric_cloudwatch(dag_id: str, priority: int, tag: DagStatus) -> None:
    get_client().put_metric_data(
        Namespace="Airflow/Custom",
        MetricData=[
            {
                "MetricName": f"priority_{tag}",
                "Dimensions": [
                    {"Name": "environment", "Value": os.environ.get("AIRFLOW_ENV_NAME", "unknown-airflow-env")},
                    {
                        "Name": "dag",
                        "Value": dag_id,
                    },
                    {
                        "Name": "priority",
                        "Value": str(priority),
                    },
                ],
                "Timestamp": datetime.utcnow(),
                "Value": int(priority),
                "Unit": "Count",
            }
        ],
    )


@hookimpl
def on_dag_run_running(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_cloudwatch(dag_id, priority, "running")


@hookimpl
def on_dag_run_success(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_cloudwatch(dag_id, priority, "success")


@hookimpl
def on_dag_run_failed(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_cloudwatch(dag_id, priority, "failed")


class AWSCloudWatchPriorityPlugin(AirflowPlugin):
    name = "AWSCloudWatchPriorityPlugin"
    listeners = []


try:
    if os.environ.get("SPHINX_BUILDING", "0") != "1":
        # Call once to ensure plugin will work
        import boto3  # noqa: F401

        get_config_option("aws", "region")
    AWSCloudWatchPriorityPlugin.listeners.append(sys.modules[__name__])
except (ImportError, AirflowPriorityConfigurationOptionNotFound):
    _log.warning("aws cloudwatch plugin could not be enabled!")
