# How to send DAG failures to Symphony

Install `airflow-priority[symphony]`. Use the certificate and key for an existing
Symphony service account and the endpoints for your deployment:

```ini
[priority.symphony]
room_name = airflow-alerts
message_create_url = https://symphony.example.com/agent/v4/stream/SID/message/create
cert_file = /etc/symphony/cert.pem
key_file = /etc/symphony/key.pem
session_auth = https://symphony-api.example.com/sessionauth/v1/authenticate
key_auth = https://symphony-api.example.com/keyauth/v1/authenticate
room_search_url = https://symphony.example.com/pod/v3/room/search
threshold = 2
```

Make the certificate files readable by the processes receiving listener events.
Restart Airflow components, then trigger a failing P1/P2 test DAG. Confirm a
message appears in the selected room. `SID` is replaced with the discovered
room ID when the sender posts the message.

Use `room_name_failed_P1` to select a separate room for urgent failures.
`send_running`, `send_success`, and `update_message` control additional posts;
Symphony update handling posts another message rather than editing the old one.
See the [messaging reference](API.md#messaging-backends) for routing and required
fields, and [troubleshooting](how-to.md#how-to-troubleshoot-missing-alerts) for
certificate authentication or room-search failures.
