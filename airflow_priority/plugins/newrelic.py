from functools import lru_cache
from json import loads
from typing import Any, Dict

from newrelic_telemetry_sdk import GaugeMetric, MetricClient

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)

DefaultMetric: str = "airflow.custom.priority"


@lru_cache
def get_client():
    return MetricClient(get_config_option("newrelic", "api_key"))


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: Dict[DagStatus, Any]) -> None:
    metric = get_config_option("newrelic", "metric", default=DefaultMetric)
    tags = loads(get_config_option("newrelic", "tags", default="{}"))
    tags = {
        "application": "airflow",
        "priority": str(priority),
        "dag": dag_id,
        **tags,
    }
    metrics = [GaugeMetric(f"{metric}.p{priority}.{tag}", 1, tags=tags)]

    if tag == "success":
        if "running" in context:
            # If the task was running before, we need to decrement the running metric
            metrics.append(
                GaugeMetric(
                    f"{metric}.p{priority}.running",
                    -1,
                    tags=tags,
                )
            )
            context.pop("running", None)
        if "failed" in context:
            # If the task was failed before, we need to decrement the failed metric
            metrics.append(GaugeMetric(f"{metric}.p{priority}.failed", -1, tags=tags))
            context.pop("failed", None)
        context.clear()
    elif tag == "failed":
        # If the task was running before, we need to decrement the running metric
        if "running" in context:
            metrics.append(GaugeMetric(f"{metric}.p{priority}.running", -1, tags=tags))
            context.pop("running", None)
        if "success" in context:
            # If the task was successful before, we need to decrement the success metric
            metrics.append(GaugeMetric(f"{metric}.p{priority}.success", -1, tags=tags))
            context.pop("success", None)
        context["failed"] = True
    elif tag == "running":
        if "success" in context:
            # If the task was successful before, we need to decrement the success metric
            metrics.append(GaugeMetric(f"{metric}.p{priority}.success", -1, tags=tags))
            context.pop("success", None)
        if "failed" in context:
            # If the task was failed before, we need to decrement the failed metric
            metrics.append(GaugeMetric(f"{metric}.p{priority}.failed", -1, tags=tags))
            context.pop("failed", None)
        context["running"] = True
    get_client().send_batch(metrics)
