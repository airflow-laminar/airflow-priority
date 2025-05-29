import os
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict

from boto3 import client as Boto3Client
from botocore.config import Config

from ..common import DagStatus, get_config_option

DefaultNamespace: str = "Airflow/Custom"
DefaultMetric: str = "priority_{tag}"


__all__ = ("send_metric",)


@lru_cache
def get_client():
    return Boto3Client("cloudwatch", config=Config(region_name=get_config_option("aws", "region"), retries=dict(max_attempts=10, mode="adaptive")))


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: Dict[DagStatus, Any]) -> None:
    namespace = get_config_option("aws", "namespace", default=DefaultNamespace)
    metric = get_config_option("aws", "metric", default=DefaultMetric)

    if "{tag}" in metric:
        metric = metric.format(tag=tag)

    client = get_client()

    # Calculate the value as an integer based on previous state

    # client.put_metric_data(Namespace=namespace, MetricData=[
    base_metric = {
        "MetricName": metric,
        "Dimensions": [
            {"Name": "environment", "Value": os.environ.get("AIRFLOW_ENV_NAME", "unknown")},
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
    metrics = [base_metric.copy()]

    if tag == "success":
        if "running" in context:
            # If the task was running before, we need to decrement the running metric
            metric_copy = base_metric.copy()
            metric_copy["MetricName"] = f"{metric}.p{priority}.running"
            metric_copy["Value"] = -1
            metrics.append(metric_copy)
            context.pop("running", None)
        if "failed" in context:
            # If the task was failed before, we need to decrement the failed metric
            metric_copy = base_metric.copy()
            metric_copy["MetricName"] = f"{metric}.p{priority}.failed"
            metric_copy["Value"] = -1
            metrics.append(metric_copy)
            context.pop("failed", None)
        context.clear()
    elif tag == "failed":
        # If the task was running before, we need to decrement the running metric
        if "running" in context:
            metric_copy = base_metric.copy()
            metric_copy["MetricName"] = f"{metric}.p{priority}.running"
            metric_copy["Value"] = -1
            metrics.append(metric_copy)
            context.pop("running", None)
        if "success" in context:
            # If the task was successful before, we need to decrement the success metric
            metric_copy = base_metric.copy()
            metric_copy["MetricName"] = f"{metric}.p{priority}.success"
            metric_copy["Value"] = -1
            metrics.append(metric_copy)
            context.pop("success", None)
        context["failed"] = True
    elif tag == "running":
        if "success" in context:
            # If the task was successful before, we need to decrement the success metric
            metric_copy = base_metric.copy()
            metric_copy["MetricName"] = f"{metric}.p{priority}.success"
            metric_copy["Value"] = -1
            metrics.append(metric_copy)
            context.pop("success", None)
        if "failed" in context:
            # If the task was failed before, we need to decrement the failed metric
            metric_copy = base_metric.copy()
            metric_copy["MetricName"] = f"{metric}.p{priority}.failed"
            metric_copy["Value"] = -1
            metrics.append(metric_copy)
            context.pop("failed", None)
        context["running"] = True

    client.put_metric_data(Namespace=namespace, MetricData=metrics)
