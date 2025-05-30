from functools import lru_cache
from time import sleep
from typing import Any, Dict

from opsgenie_sdk import (
    AcknowledgeAlertPayload,
    AlertApi,
    ApiClient,
    ApiException,
    CloseAlertPayload,
    Configuration,
    CreateAlertPayload,
    SuccessResponse,
)

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)

DefaultMetric: str = "airflow.custom.priority"


@lru_cache
def get_configuration():
    conf = Configuration()
    conf.api_key["Authorization"] = get_config_option("opsgenie", "api_key")


@lru_cache
def get_client():
    conf = get_configuration()
    api_client = ApiClient(configuration=conf)
    alert_api = AlertApi(api_client=api_client)
    return alert_api


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: Dict[DagStatus, Any]) -> None:
    alert_api = get_client()

    message = f'A P{priority} DAG "{dag_id}" has been marked "{tag}"'
    entity = get_config_option("opsgenie", "entity", default="airflow.priority.dag.{priority}.{tag}")
    update_message = get_config_option("opsgenie", "update", default="true").lower() == "true"

    if "{tag}" in entity and "{priority}" in entity:
        entity = entity.format(tag=tag, priority=priority)
    elif "{tag}" in entity:
        entity = entity.format(tag=tag)
    elif "{priority}" in entity:
        entity = entity.format(priority=priority)

    alert = CreateAlertPayload(
        message=message, description=message, tags=["airflow", "dag", dag_id, "priority", tag], entity=entity, priority=f"P{priority}"
    )

    if tag == "failed":
        create_response = alert_api.create_alert(create_alert_payload=alert)
        if not isinstance(create_response, SuccessResponse):
            raise RuntimeError(f"Failed to create alert: {create_response}")
        for _ in range(5):
            try:
                response = alert_api.get_request_status(request_id=create_response.request_id)
            except ApiException:
                sleep(1)
            else:
                break
        else:
            raise RuntimeError(f"Failed to get request status for alert creation: {create_response.request_id}")
        context[tag] = response.data.alert_id

    # Update the failure message
    if tag != "failed" and update_message and "failed" in context:
        failed_context_id = context["failed"]

        if tag == "running":
            # acknowledge the alert
            acknowledge_response: SuccessResponse = alert_api.acknowledge_alert(
                identifier=failed_context_id, acknowledge_alert_payload=AcknowledgeAlertPayload(note=tag)
            )
            if not isinstance(acknowledge_response, SuccessResponse):
                raise RuntimeError(f"Failed to acknowledge alert: {acknowledge_response}")
            for _ in range(5):
                try:
                    response = alert_api.get_request_status(request_id=acknowledge_response.request_id)
                except ApiException:
                    sleep(1)
                else:
                    break
            else:
                raise RuntimeError(f"Failed to get request status for alert creation: {acknowledge_response.request_id}")
            context[tag] = response.data.alert_id

        if tag == "success":
            # close the alert
            close_response: SuccessResponse = alert_api.close_alert(identifier=failed_context_id, close_alert_payload=CloseAlertPayload(note=tag))
            if not isinstance(close_response, SuccessResponse):
                raise RuntimeError(f"Failed to close alert: {close_response}")
            for _ in range(5):
                try:
                    response = alert_api.get_request_status(request_id=close_response.request_id)
                except ApiException:
                    sleep(1)
                else:
                    break
            else:
                raise RuntimeError(f"Failed to get request status for alert creation: {close_response.request_id}")
            context[tag] = response.data.alert_id

    # On success, blank out the context
    if tag == "success":
        context.clear()
