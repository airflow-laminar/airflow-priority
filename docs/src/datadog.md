# Datadog

<img src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/datadog.png" width=400 alt="Datadog metric for failed DAG run">

Create a new Datadog api key [following their guide](https://docs.datadoghq.com/account_management/api-app-keys/#add-an-api-key-or-client-token).

Copy this api key into your `airflow.cfg` like so:

```
[priority.datadog]
api_key = the api key
host = https://api.datadoghq.com  # Optional host change
metric = my.custom.metric  # Optional metric name override, default is "airflow.custom.priority"
```

Ensure your dags are configured with tags and run some, it can often be convenient to have an intentionally failing `P1` dag to test the integration. With this, you can now [create custom monitors](https://docs.datadoghq.com/getting_started/monitors/) for the tags.
