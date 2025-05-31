# Discord

<img src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/discord.png" width=600 alt="Message in Discord reflecting DAG status">

Discord integration will create new messages when a DAG fails, and optionally update those messages when a DAG reruns/succeeds.

## Setup

Create a new Discord application following the [guide from the discord.py library](https://discordpy.readthedocs.io/en/stable/discord.html).

Copy the bot token somewhere secure.

## Configuration

- `token`: (**Required**) the bot token from above
- `channel`: (**Required**) channel name to send messages to
- `threshold`: (Optional) Maximum alert threshold. Alerts with higher numerical priority (lower logical priority) will be ignored
- `update_message`: (Optional) Update a failure message with running/succeeds. Defaults to `false`
- `send_running`: (Optional) Send new messages when a DAG starts running. Defaults to `false`
- `send_success`: (Optional) Send new messages when a DAG succeeds. Defaults to `false`
- `failed_color`: (Optional) Color of a DAG failed message
- `running_color`: (Optional) Color of a DAG running message.
- `success_color`: (Optional) Color of a DAG success message.
- `channel_P1`: (Optional) P1 channel override
- `channel_P2`: (Optional) P2 channel override
- `channel_P3`: (Optional) P3 channel override
- `channel_P4`: (Optional) P4 channel override
- `channel_P5`: (Optional) P5 channel override
- `channel_failed`: (Optional) Failed channel override
- `channel_success`: (Optional) Success channel override
- `channel_running`: (Optional) Running channel override
- `channel_failed_P1`: (Optional) Failed P1 channel override
- `channel_failed_P2`: (Optional) Failed P2 channel override
- `channel_failed_P3`: (Optional) Failed P3 channel override
- `channel_failed_P4`: (Optional) Failed P4 channel override
- `channel_failed_P5`: (Optional) Failed P5 channel override
- `channel_success_P1`: (Optional) Success P1 channel override
- `channel_success_P2`: (Optional) Success P2 channel override
- `channel_success_P3`: (Optional) Success P3 channel override
- `channel_success_P4`: (Optional) Success P4 channel override
- `channel_success_P5`: (Optional) Success P5 channel override
- `channel_running_P1`: (Optional) Running P1 channel override
- `channel_running_P2`: (Optional) Running P2 channel override
- `channel_running_P3`: (Optional) Running P3 channel override
- `channel_running_P4`: (Optional) Running P4 channel override
- `channel_running_P5`: (Optional) Running P5 channel override

```
[priority.discord]
token = the bot's token
channel = the numerical channel ID, from the url or by right clicking

# Configure tag and priority specific channels
channel_P3 = ...
channel_failed_P1 = ...
```

Ensure your bot is invited into any private channels.

## Verbose updates

By default, only DAG failure events will be sent.
On rerun, failure messages can be updated to reflect running/success.

The plugin can also be configured to always send updates, including when a DAG starts running and/or succeeds.
These can also be configured to send to different channels.

```
[priority.discord]
# Update messages to reflect current state
update_message = true

send_success = true
channel_success = a-different-channel
send_running = true
channel_running = a-different-channel
```

## Customizing message colors

```
[priority.discord]
failed_color = "#FF0000"
running_color = "#FFFF00"
success_color = "#00FF00"
```
