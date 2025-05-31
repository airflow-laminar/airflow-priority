from functools import lru_cache
from ssl import CERT_NONE, create_default_context
from typing import Any, Dict

from slack_sdk import WebClient

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)


@lru_cache
def get_client() -> WebClient:
    if get_config_option("slack", "nossl", default="false").lower() == "true":
        unsafe_context = create_default_context()
        unsafe_context.check_hostname = False
        unsafe_context.verify_mode = CERT_NONE
        return WebClient(token=get_config_option("slack", "token"), ssl=unsafe_context)
    return WebClient(token=get_config_option("slack", "token"))


@lru_cache
def get_channel_id(tag: DagStatus, priority: int) -> str:
    # First, grab the default channel
    channel_name = get_config_option("slack", "channel", default="")

    # Next, grab the channel name for the tag, if it exists
    channel_name = get_config_option("slack", f"channel_{tag}", default=channel_name)

    # Try the channel name for the priority, if it exists
    channel_name = get_config_option("slack", f"channel_P{priority}", default=channel_name)

    # And finally, try the channel name for tag + priority, if it exists
    channel_name = get_config_option("slack", f"channel_{tag}_P{priority}", default=channel_name)

    # Lookup the channel ID
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
        channel = get_channel_id(tag, priority)
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
        channel = get_channel_id("failed", priority)
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
