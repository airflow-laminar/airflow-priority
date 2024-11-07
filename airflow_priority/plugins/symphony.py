import os
import ssl
import sys
from functools import lru_cache
from logging import getLogger

from airflow.listeners import hookimpl
from airflow.models.dagrun import DagRun
from airflow.plugins_manager import AirflowPlugin

from airflow_priority import AirflowPriorityConfigurationOptionNotFound, DagStatus, get_config_option, has_priority_tag

__all__ = ("get_config_options", "get_headers", "get_room_id", "send_metric_symphony", "on_dag_run_failed", "SymphonyPriorityPlugin")


_log = getLogger(__name__)


@lru_cache
def get_config_options():
    return {
        "room_name": get_config_option("symphony", "room_name"),
        "message_create_url": get_config_option("symphony", "message_create_url"),
        "cert_file": get_config_option("symphony", "cert_file"),
        "key_file": get_config_option("symphony", "key_file"),
        "session_auth": get_config_option("symphony", "session_auth"),
        "key_auth": get_config_option("symphony", "key_auth"),
        "room_search_url": get_config_option("symphony", "room_search_url"),
    }


def _client_cert_post(url: str, cert_file: str, key_file: str) -> str:
    from httpx import post

    context = ssl.SSLContext(ssl.PROTOCOL_SSLv23)
    context.load_cert_chain(certfile=cert_file, keyfile=key_file)
    response = post(url=url, verify=context, headers={"Content-Type": "application/json"}, data="{}")
    if response.status_code != 200:
        raise Exception(f"Cannot connect for symphony handshake to {url}: {response.status_code}")
    return response.json()


@lru_cache
def get_headers():
    config_options = get_config_options()
    session_token = _client_cert_post(config_options["session_auth"], config_options["cert_file"], config_options["key_file"])["token"]
    key_manager_token = _client_cert_post(config_options["key_auth"], config_options["cert_file"], config_options["key_file"])["token"]
    return {
        "sessionToken": session_token,
        "keyManagerToken": key_manager_token,
        "Accept": "application/json",
    }


@lru_cache
def get_room_id():
    from httpx import post

    config_options = get_config_options()

    res = post(
        url=config_options["room_search_url"],
        json={"query": config_options["room_name"]},
        headers=get_headers(),
    )
    if res and res.status_code == 200:
        for room in res.json()["rooms"]:
            name = room.get("roomAttributes", {}).get("name")
            if name and name == config_options["room_name"]:
                return room.get("roomSystemInfo", {}).get("id")
    raise Exception("TODO")


def send_metric_symphony(dag_id: str, priority: int, tag: DagStatus) -> None:
    from httpx import post

    return post(
        url=get_config_options()["message_create_url"].replace("SID", get_room_id()),
        json={"message": f'<messageML>A P{priority} DAG "{dag_id}" has {tag}!</messageML>'},
        headers=get_headers(),
    )


# @hookimpl
# def on_dag_run_running(dag_run: DagRun, msg: str):
#     dag_id, priority = has_priority_tag(dag_run=dag_run)
#     if priority:
#         send_metric_slack(dag_id, priority, "running")


# @hookimpl
# def on_dag_run_success(dag_run: DagRun, msg: str):
#     dag_id, priority = has_priority_tag(dag_run=dag_run)
#     if priority:
#         send_metric_slack(dag_id, priority, "succeeded")


@hookimpl
def on_dag_run_failed(dag_run: DagRun, msg: str):
    dag_id, priority = has_priority_tag(dag_run=dag_run)
    if priority:
        send_metric_symphony(dag_id, priority, "failed")


class SymphonyPriorityPlugin(AirflowPlugin):
    name = "SymphonyPriorityPlugin"
    listeners = []


try:
    if os.environ.get("SPHINX_BUILDING", "0") != "1":
        # Call once to ensure plugin will work
        import httpx  # noqa: F401

        get_config_options()
    SymphonyPriorityPlugin.listeners.append(sys.modules[__name__])
except (ImportError, AirflowPriorityConfigurationOptionNotFound):
    _log.warning("symphony plugin could not be enabled! Ensure `httpx` is installed and all configuration options are set.")
