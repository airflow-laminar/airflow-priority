import ssl
from functools import lru_cache
from typing import Any, Dict

from httpx import post

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)


@lru_cache
def get_config_options():
    return {
        "message_create_url": get_config_option("symphony", "message_create_url"),
        "cert_file": get_config_option("symphony", "cert_file"),
        "key_file": get_config_option("symphony", "key_file"),
        "session_auth": get_config_option("symphony", "session_auth"),
        "key_auth": get_config_option("symphony", "key_auth"),
        "room_search_url": get_config_option("symphony", "room_search_url"),
    }


def _client_cert_post(url: str, cert_file: str, key_file: str) -> str:
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
def get_room_id(tag: DagStatus, priority: int) -> str:
    config_options = get_config_options()

    # First, grab the default channel
    channel_name = get_config_option("symphony", "room_name", default="")

    # Next, grab the channel name for the tag, if it exists
    channel_name = get_config_option("symphony", f"room_name_{tag}", default=channel_name)

    # Try the channel name for the priority, if it exists
    channel_name = get_config_option("symphony", f"room_name_P{priority}", default=channel_name)

    # And finally, try the channel name for tag + priority, if it exists
    channel_name = get_config_option("symphony", f"room_name_{tag}_P{priority}", default=channel_name)

    res = post(
        url=config_options["room_search_url"],
        json={"query": channel_name},
        headers=get_headers(),
    )
    if res and res.status_code == 200:
        for room in res.json()["rooms"]:
            name = room.get("roomAttributes", {}).get("name")
            if name and name == config_options["room_name"]:
                return room.get("roomSystemInfo", {}).get("id")
    raise Exception("TODO")


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: Dict[DagStatus, Any]) -> None:
    send_running = get_config_option("symphony", "send_running", default="false").lower() == "true"
    send_success = get_config_option("symphony", "send_success", default="false").lower() == "true"
    update_message = get_config_option("symphony", "update_message", default="false").lower() == "true"

    if tag == "failed" or (tag == "running" and send_running) or (tag == "success" and send_success):
        # Send a message to the corresponding channel
        context[tag] = post(
            url=get_config_options()["message_create_url"].replace("SID", get_room_id(tag, priority)),
            json={"message": f'<messageML>A P{priority} DAG "{dag_id}" has been marked "{tag}"</messageML>'},
            headers=get_headers(),
        )

    # Update the failure message
    if tag != "failed" and update_message and "failed" in context:
        # Update the message for the failed DAG
        context["failed"] = post(
            url=get_config_options()["message_create_url"].replace("SID", get_room_id("failed", priority)),
            json={"message": f'<messageML>A P{priority} DAG "{dag_id}" has been marked "{tag}"</messageML>'},
            headers=get_headers(),
        )

    # On success, blank out the context
    if tag == "success":
        context.clear()
