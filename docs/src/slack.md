# How to send DAG failures to Slack

Install `airflow-priority[slack]` in the Airflow environment. Use a bot installed
in the workspace and invited to the destination channel. Enable `channels:read`,
`groups:read`, and `chat:write` permissions for channel lookup and posting; see
Slack's [listing](https://docs.slack.dev/reference/methods/conversations.list/)
and [message](https://docs.slack.dev/reference/methods/chat.postMessage/) APIs.

Configure the scheduler and API server:

```ini
[priority.slack]
token = YOUR_BOT_TOKEN
channel = airflow-alerts
threshold = 2
```

Use the channel name without `#`. Restart Airflow components, then trigger a
P1 or P2 test DAG that fails. Inspect the Airflow listener logs and destination
channel. Follow the [tutorial](tutorial.md) for a complete test DAG.

To route urgent failures separately, add:

```ini
[priority.slack]
channel_failed_P1 = urgent-airflow
```

Enable `send_running` or `send_success` to create messages for those states.
Enable `update_message` to update a stored failure message when the same run
changes state in the same process. See the
[messaging reference](API.md#messaging-backends) for defaults and routing precedence,
and [troubleshooting](how-to.md#how-to-troubleshoot-missing-alerts) for delivery errors.
