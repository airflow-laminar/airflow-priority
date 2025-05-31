from functools import lru_cache
from typing import Any, Dict

from pagerduty import EventsApiV2Client

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)

DefaultMetric: str = "airflow.priority"


@lru_cache
def get_client() -> EventsApiV2Client:
    return EventsApiV2Client(api_key=get_config_option("pagerduty", "routing_key"))


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: Dict[DagStatus, Any]) -> None:
    client = get_client()

    summary = f'A P{priority} DAG "{dag_id}" has been marked "{tag}"'
    source = get_config_option("pagerduty", "source", default="airflow.priority.dag.{priority}.{tag}")
    update_message = get_config_option("pagerduty", "update", default="true").lower() == "true"

    if "{tag}" in source and "{priority}" in source:
        source = source.format(tag=tag, priority=priority)
    elif "{tag}" in source:
        source = source.format(tag=tag)
    elif "{priority}" in source:
        source = source.format(priority=priority)

    if tag == "failed":
        create_dedup_key = client.trigger(summary=summary, source=source, severity=f"SEV-{priority}")
        context[tag] = create_dedup_key

    # Update the failure message
    if tag != "failed" and update_message and "failed" in context:
        failed_dedup_key = context["failed"]

        if tag == "running":
            # acknowledge the alert
            client.acknowledge(failed_dedup_key)
            context[tag] = failed_dedup_key

        if tag == "success":
            # close the alert
            client.resolve(failed_dedup_key)
            context[tag] = failed_dedup_key

    # On success, blank out the context
    if tag == "success":
        context.clear()
