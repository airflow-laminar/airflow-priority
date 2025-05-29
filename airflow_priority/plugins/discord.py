from asyncio import sleep
from functools import lru_cache
from queue import Queue
from threading import Thread
from typing import Any, Dict, Optional

from discord import Client, Color, Embed, Intents, Message, TextChannel

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)


@lru_cache
def get_client():
    client = Client(intents=Intents.default())
    client.inqueue = Queue()
    client.outqueue = Queue()

    @client.event
    async def on_ready():
        channel: TextChannel
        msg: Message
        new_msg: Optional[str]

        while True:
            while client.outqueue.empty():
                await sleep(5)

            channel, msg, new_msg, color = client.outqueue.get()

            if new_msg is None:
                channel_inst = client.get_channel(channel)
                client.inqueue.put(await channel_inst.send(embed=Embed(description=msg, color=Color.from_str(color))))
            else:
                client.inqueue.put(await msg.edit(embed=Embed(description=new_msg, color=Color.from_str(color))))

    token = get_config_option("discord", "token")
    t = Thread(target=client.run, args=(token,), daemon=True)
    t.start()
    return client


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: Dict[DagStatus, Any]) -> None:
    send_running = get_config_option("discord", "send_running", default="false").lower() == "true"
    send_success = get_config_option("discord", "send_success", default="false").lower() == "true"
    update_message = get_config_option("discord", "update_message", default="false").lower() == "true"

    running_color = get_config_option("discord", "running_color", default="#ffff00")
    failed_color = get_config_option("discord", "failed_color", default="#ff0000")
    success_color = get_config_option("discord", "success_color", default="#00ff00")

    default_channel = get_config_option("discord", "channel")
    channel = int(get_config_option("discord", f"channel_{tag}", default=default_channel))

    client = get_client()
    client_out_queue = client.outqueue
    client_in_queue = client.inqueue

    if tag == "failed" or (tag == "running" and send_running) or (tag == "success" and send_success):
        # Send a message to the corresponding channel
        client_out_queue.put(
            (
                channel,
                f'A P{priority} DAG "{dag_id}" has been marked "{tag}"',
                None,
                running_color if tag == "running" else failed_color if tag == "failed" else success_color,
            )
        )
        context[tag] = client_in_queue.get()

    # Update the failure message
    if tag != "failed" and update_message and "failed" in context:
        channel = int(get_config_option("discord", "channel_failed", default=default_channel))
        failed_context = context["failed"]
        client_out_queue.put(
            (
                channel,
                failed_context,
                f'A P{priority} DAG "{dag_id}" has been marked "{tag}"',
                running_color if tag == "running" else success_color,
            )
        )
        context["failed"] = client_in_queue.get()

    # On success, blank out the context
    if tag == "success":
        context.clear()
