# Slack

<img src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/slack.png" width=400 alt="Message in Slack reflecting DAG status">

Configure a new slack application following the [Slack Quickstart](https://api.slack.com/quickstart).

Ensure your application has the following scopes for public and private channel access:

- `channels:read`
- `groups:read`
- `chat:write`

Enable and install your Slack application into your workspace, and add it as an integration in whatever channel you want it to post.

Copy your Slack application's Oauth Token (starting with `xoxb-`) and your desired channel into your `airflow.cfg` like so:

```
[priority.slack]
token = xoxb-...
channel = channel-name

# Configure tag and priority specific channels
channel_P3 = ...
channel_failed_P1 = ...
```

## Verbose updates

By default, only DAG failure events will be sent.
On rerun, failure messages can be updated to reflect running/success.

The plugin can also be configured to always send updates, including when a DAG starts running and/or succeeds.
These can also be configured to send to different channels.

```
[priority.slack]
# Update messages to reflect current state
update_message = true

send_success = true
channel_success = a-different-channel
send_running = true
channel_running = a-different-channel
```

## Customizing message colors

```
[priority.slack]
failed_color = "#FF0000"
running_color = "#FFFF00"
success_color = "#00FF00"
```
