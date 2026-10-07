# How to publish DAG status metrics to Datadog

Install `airflow-priority[datadog]`. Obtain an API key and select the API base
URL for your Datadog site, then configure the Airflow components:

```ini
[priority.datadog]
api_key = YOUR_API_KEY
host = https://api.datadoghq.com
metric = airflow.priority
tags = environment:production
threshold = 2
```

Use an API URL, not the web application hostname. In airflow-config YAML,
provide `tags` as a list, such as `[environment:production]`.

Restart the components and trigger a failing P1/P2 test DAG. Find
`airflow.priority.p1.failed` or `airflow.priority.p2.failed` in Datadog's metric
explorer, filtered by its `dag` tag. The metric name uses `failed`, `running`,
and `success` state suffixes.

Configure an external monitor on the failure sample for the priorities you
route. Choose its evaluation window and recovery behavior for your workflow's
cadence; these samples are not a persistent count of failed DAGs. See the
[metric reference](API.md#metric-backends) for fields and observed-state adjustments.
