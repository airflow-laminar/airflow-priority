import os
import sys
from datetime import datetime
from functools import lru_cache
from logging import getLogger

from airflow.listeners import hookimpl
from airflow.models.dagrun import DagRun
from airflow.plugins_manager import AirflowPlugin

from airflow_priority import AirflowPriorityConfigurationOptionNotFound, DagStatus, get_config_option, has_priority_tag

__all__ = (
    "send_metric_datadog",
    "on_dag_run_running",
    "on_dag_run_success",
    "on_dag_run_failed",
    "DatadogPriorityPlugin",
)

_log = getLogger(__name__)


@lru_cache
def get_configuration():
    from datadog_api_client import Configuration

    return Configuration(
        api_key={"apiKeyAuth": get_config_option("datadog", "api_key")},
    )


def send_metric_datadog(dag_id: str, priority: int, tag: DagStatus) -> None:
    from datadog_api_client import ApiClient
    from datadog_api_client.v2.api.metrics_api import MetricsApi
    from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
    from datadog_api_client.v2.model.metric_payload import MetricPayload
    from datadog_api_client.v2.model.metric_point import MetricPoint
    from datadog_api_client.v2.model.metric_resource import MetricResource
    from datadog_api_client.v2.model.metric_series import MetricSeries

    with ApiClient(get_configuration()) as api_client:
        api_instance = MetricsApi(api_client)

        body = MetricPayload(
            series=[
                MetricSeries(
                    metric=f"airflow.custom.priority.p{priority}.{tag}",
                    type=MetricIntakeType.UNSPECIFIED,
                    points=[
                        MetricPoint(
                            timestamp=int(datetime.now().timestamp()),
                            value=priority,
                        ),
                    ],
                    resources=[
                        MetricResource(
                            name=dag_id,
                            type="dag",
                        ),
                    ],
                    tags=["airflow", "priority", f"dag_{dag_id}"],
                ),
            ],
        )

        resp = api_instance.submit_metrics(body=body)
        assert resp["errors"] == []


@hookimpl
def on_dag_run_running(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_datadog(dag_id, priority, "running")


@hookimpl
def on_dag_run_success(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_datadog(dag_id, priority, "success")


@hookimpl
def on_dag_run_failed(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_datadog(dag_id, priority, "failed")


class DatadogPriorityPlugin(AirflowPlugin):
    name = "DatadogPriorityPlugin"
    listeners = []


try:
    if os.environ.get("SPHINX_BUILDING", "0") != "1":
        # Call once to ensure plugin will work
        get_configuration()
        get_config_option("datadog", "api_key")
    DatadogPriorityPlugin.listeners.append(sys.modules[__name__])
except (ImportError, AirflowPriorityConfigurationOptionNotFound):
    _log.warning("datadog plugin could not be enabled! Ensure `datadog-api-client` is installed and all configuration options are set.")
