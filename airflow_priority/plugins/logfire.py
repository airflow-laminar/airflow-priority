from functools import lru_cache
from typing import Any, Dict

import logfire

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)


DefaultMetric = "airflow.priority"


@lru_cache
def get_client():
    token = get_config_option("logfire", "token")
    environment = get_config_option("logfire", "environment", required=False)
    return logfire.configure(
        token=token,
        environment=environment,
    )


@lru_cache
def get_gauges():
    client = get_client()
    metric = get_config_option("logfire", "metric", default=DefaultMetric)
    return {
        ("success", 1): client.metric_gauge(name=f"{metric}.p1.success"),
        ("success", 2): client.metric_gauge(name=f"{metric}.p2.success"),
        ("success", 3): client.metric_gauge(name=f"{metric}.p3.success"),
        ("success", 4): client.metric_gauge(name=f"{metric}.p4.success"),
        ("success", 5): client.metric_gauge(name=f"{metric}.p5.success"),
        ("failed", 1): client.metric_gauge(name=f"{metric}.p1.failed"),
        ("failed", 2): client.metric_gauge(name=f"{metric}.p2.failed"),
        ("failed", 3): client.metric_gauge(name=f"{metric}.p3.failed"),
        ("failed", 4): client.metric_gauge(name=f"{metric}.p4.failed"),
        ("failed", 5): client.metric_gauge(name=f"{metric}.p5.failed"),
        ("running", 1): client.metric_gauge(name=f"{metric}.p1.running"),
        ("running", 2): client.metric_gauge(name=f"{metric}.p2.running"),
        ("running", 3): client.metric_gauge(name=f"{metric}.p3.running"),
        ("running", 4): client.metric_gauge(name=f"{metric}.p4.running"),
        ("running", 5): client.metric_gauge(name=f"{metric}.p5.running"),
    }


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: Dict[DagStatus, Any]) -> None:
    gauges = get_gauges()

    gauges[(tag, priority)].set(1)

    if tag == "success":
        if "running" in context:
            # If the task was running before, we need to decrement the running metric
            gauges[("running", priority)].set(-1)
            context.pop("running", None)
        if "failed" in context:
            # If the task was failed before, we need to decrement the failed metric
            gauges[("failed", priority)].set(-1)
            context.pop("failed", None)
        context.clear()
    elif tag == "failed":
        # If the task was running before, we need to decrement the running metric
        if "running" in context:
            gauges[("running", priority)].set(-1)
            context.pop("running", None)
        if "success" in context:
            # If the task was successful before, we need to decrement the success metric
            gauges[("success", priority)].set(-1)
            context.pop("success", None)
        context["failed"] = True
    elif tag == "running":
        if "success" in context:
            # If the task was successful before, we need to decrement the success metric
            gauges[("success", priority)].set(-1)
            context.pop("success", None)
        if "failed" in context:
            # If the task was failed before, we need to decrement the failed metric
            gauges[("failed", priority)].set(-1)
            context.pop("failed", None)
        context["running"] = True
