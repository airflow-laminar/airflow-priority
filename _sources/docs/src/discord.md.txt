# Discord

<img src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/discord.png" width=400 alt="Message in Discord reflecting DAG status">

Create a new Discord application following the [guide from the discord.py library](https://discordpy.readthedocs.io/en/stable/discord.html).

Copy your bot's token into your `airflow.cfg` like so:

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
