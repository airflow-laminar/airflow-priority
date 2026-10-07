# How to send DAG failures to Discord

Install `airflow-priority[discord]`. Use an existing Discord bot with access to
send messages and embeds in the destination channel. Configure its bot token
and the numeric channel ID:

```ini
[priority.discord]
token = YOUR_BOT_TOKEN
channel = 123456789012345678
threshold = 2
```

Restart Airflow components and trigger a failing P1/P2 test DAG. Confirm the
failure embed appears in that channel. Use the channel's ID, rather than its
name, for overrides such as `channel_failed_P1`.

The Discord client runs in a background thread; the sender waits for a queue
response. Keep the bot connected when testing delivery. See the
[messaging reference](API.md#messaging-backends) for optional state notifications,
colors, and the limits of same-run message updates.
