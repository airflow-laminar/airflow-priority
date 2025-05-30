from datetime import datetime
from functools import lru_cache
from typing import Any, Dict

from datadog_api_client import ApiClient, Configuration
from datadog_api_client.v2.api.metrics_api import MetricsApi
from datadog_api_client.v2.model.metric_intake_type import MetricIntakeType
from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_resource import MetricResource
from datadog_api_client.v2.model.metric_series import MetricSeries

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)

DefaultMetric: str = "airflow.custom.priority"


@lru_cache
def get_configuration():
    return Configuration(
        host=get_config_option("datadog", "host", default="https://api.datadoghq.com"),
        api_key={"apiKeyAuth": get_config_option("datadog", "api_key")},
    )


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: Dict[DagStatus, Any]) -> None:
    metric = get_config_option("datadog", "metric", default=DefaultMetric)
    tags = get_config_option("datadog", "tags", default="").split(",")
    tags = ["application:airflow", f"priority:{priority}", f"dag:{dag_id}", *tags]

    with ApiClient(get_configuration()) as api_client:
        api_instance = MetricsApi(api_client)
        metrics = [
            MetricSeries(
                metric=f"{metric}.p{priority}.{tag}",
                type=MetricIntakeType.GAUGE,
                points=[
                    MetricPoint(
                        timestamp=int(datetime.now().timestamp()),
                        value=1,
                    ),
                ],
                resources=[
                    MetricResource(
                        name=dag_id,
                        type="dag",
                    ),
                ],
                tags=tags,
            )
        ]

        if tag == "success":
            if "running" in context:
                # If the task was running before, we need to decrement the running metric
                metrics.append(
                    MetricSeries(
                        metric=f"{metric}.p{priority}.running",
                        type=MetricIntakeType.GAUGE,
                        points=[
                            MetricPoint(
                                timestamp=int(datetime.now().timestamp()),
                                value=-1,
                            ),
                        ],
                        resources=[
                            MetricResource(
                                name=dag_id,
                                type="dag",
                            ),
                        ],
                        tags=tags,
                    )
                )
                context.pop("running", None)
            if "failed" in context:
                # If the task was failed before, we need to decrement the failed metric
                metrics.append(
                    MetricSeries(
                        metric=f"{metric}.p{priority}.failed",
                        type=MetricIntakeType.GAUGE,
                        points=[
                            MetricPoint(
                                timestamp=int(datetime.now().timestamp()),
                                value=-1,
                            ),
                        ],
                        resources=[
                            MetricResource(
                                name=dag_id,
                                type="dag",
                            ),
                        ],
                        tags=tags,
                    )
                )
                context.pop("failed", None)
            context.clear()
        elif tag == "failed":
            # If the task was running before, we need to decrement the running metric
            if "running" in context:
                metrics.append(
                    MetricSeries(
                        metric=f"{metric}.p{priority}.running",
                        type=MetricIntakeType.GAUGE,
                        points=[
                            MetricPoint(
                                timestamp=int(datetime.now().timestamp()),
                                value=-1,
                            ),
                        ],
                        resources=[
                            MetricResource(
                                name=dag_id,
                                type="dag",
                            ),
                        ],
                        tags=tags,
                    )
                )
                context.pop("running", None)
            if "success" in context:
                # If the task was successful before, we need to decrement the success metric
                metrics.append(
                    MetricSeries(
                        metric=f"{metric}.p{priority}.success",
                        type=MetricIntakeType.GAUGE,
                        points=[
                            MetricPoint(
                                timestamp=int(datetime.now().timestamp()),
                                value=-1,
                            ),
                        ],
                        resources=[
                            MetricResource(
                                name=dag_id,
                                type="dag",
                            ),
                        ],
                        tags=tags,
                    )
                )
                context.pop("success", None)
            context["failed"] = True
        elif tag == "running":
            if "success" in context:
                # If the task was successful before, we need to decrement the success metric
                metrics.append(
                    MetricSeries(
                        metric=f"{metric}.p{priority}.success",
                        type=MetricIntakeType.GAUGE,
                        points=[
                            MetricPoint(
                                timestamp=int(datetime.now().timestamp()),
                                value=-1,
                            ),
                        ],
                        resources=[
                            MetricResource(
                                name=dag_id,
                                type="dag",
                            ),
                        ],
                        tags=tags,
                    )
                )
                context.pop("success", None)
            if "failed" in context:
                # If the task was failed before, we need to decrement the failed metric
                metrics.append(
                    MetricSeries(
                        metric=f"{metric}.p{priority}.failed",
                        type=MetricIntakeType.GAUGE,
                        points=[
                            MetricPoint(
                                timestamp=int(datetime.now().timestamp()),
                                value=-1,
                            ),
                        ],
                        resources=[
                            MetricResource(
                                name=dag_id,
                                type="dag",
                            ),
                        ],
                        tags=tags,
                    )
                )
                context.pop("failed", None)
            context["running"] = True
        resp = api_instance.submit_metrics(body=MetricPayload(series=metrics))
        assert resp["errors"] == []
