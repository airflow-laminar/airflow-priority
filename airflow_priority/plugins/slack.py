from functools import lru_cache
from typing import Any, Dict

from slack_sdk import WebClient

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)


@lru_cache
def get_client() -> WebClient:
    return WebClient(token=get_config_option("slack", "token"))


@lru_cache
def get_channel_id(tag: DagStatus) -> str:
    default_channel_name = get_config_option("slack", "channel")
    channel_name = get_config_option("slack", f"channel_{tag}", default=default_channel_name)
    conversations = get_client().conversations_list(types=["public_channel", "private_channel"])
    if conversations.data["ok"]:
        for channel in conversations.data["channels"]:
            if channel["name"] == channel_name:
                return channel["id"]
    raise Exception("TODO")


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: Dict[DagStatus, Any]) -> None:
    send_running = get_config_option("slack", "send_running", default="false").lower() == "true"
    send_success = get_config_option("slack", "send_success", default="false").lower() == "true"
    update_message = get_config_option("slack", "update_message", default="false").lower() == "true"

    running_color = get_config_option("slack", "running_color", default="#ffff00")
    failed_color = get_config_option("slack", "failed_color", default="#ff0000")
    success_color = get_config_option("slack", "success_color", default="#00ff00")

    client = get_client()

    if tag == "failed" or (tag == "running" and send_running) or (tag == "success" and send_success):
        # Send a message to the corresponding channel
        channel = get_channel_id(tag)
        context[tag] = client.chat_postMessage(
            channel=channel,
            attachments=[
                {
                    "mrkdwn_in": ["text"],
                    "text": f'A P{priority} DAG "{dag_id}" has been marked "{tag}"',
                    "color": running_color if tag == "running" else failed_color if tag == "failed" else success_color,
                }
            ],
        )

    # Update the failure message
    if tag != "failed" and update_message and "failed" in context:
        channel = get_channel_id("failed")
        failed_context = context["failed"]
        failed_message_ts = failed_context.get("ts")
        if failed_message_ts:
            # Update the message for the failed DAG
            client.chat_update(
                channel=channel,
                ts=failed_message_ts,
                attachments=[
                    {
                        "mrkdwn_in": ["text"],
                        "color": running_color if tag == "running" else success_color,
                        "text": f'A P{priority} DAG "{dag_id}" has been marked "{tag}"',
                    }
                ],
            )

    # On success, blank out the context
    if tag == "success":
        context.clear()
