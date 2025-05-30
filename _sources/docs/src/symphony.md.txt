# Symphony

Documentation coming soon!

- [Overview of REST API](https://docs.developers.symphony.com/bots/overview-of-rest-api)
- [Certificate Authentication Workflow](https://docs.developers.symphony.com/bots/authentication/certificate-authentication)

```
[priority.symphony]
room_name = the room name
message_create_url = https://mycompany.symphony.com/agent/v4/stream/SID/message/create
cert_file = path/to/my/cert.pem
key_file = path/to/my/key.pem
session_auth = https://mycompany-api.symphony.com/sessionauth/v1/authenticate
key_auth = https://mycompany-api.symphony.com/keyauth/v1/authenticate
room_search_url = https://mycompany.symphony.com/pod/v3/room/search
```
