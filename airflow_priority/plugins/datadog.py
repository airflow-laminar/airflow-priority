import sys
from datetime import datetime
from functools import lru_cache

from airflow.listeners import hookimpl
from airflow.models.dagrun import DagRun
from airflow.plugins_manager import AirflowPlugin
from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_resource import MetricResource
from datadog_api_client.v2.model.metric_series import MetricSeries

from airflow_priority import DagStatus, get_config_option, has_priority_tag


@lru_cache
def get_configuration():
    return Configuration(
        api_key={"apiKeyAuth": get_config_option("datadog", "api_key", "")},
    )


def send_metric_datadog(dag_id: str, priority: int, tag: DagStatus) -> None:
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
    listeners = [sys.modules[__name__]]
