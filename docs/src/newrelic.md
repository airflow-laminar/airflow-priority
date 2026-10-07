# How to publish DAG status metrics to New Relic

Install `airflow-priority[newrelic]` and provide the ingest key for your New Relic
account:

```ini
[priority.newrelic]
api_key = YOUR_INGEST_KEY
metric = airflow.priority
tags = {"environment": "production"}
threshold = 2
```

INI tags use a JSON object; airflow-config YAML tags use a mapping.
Restart Airflow components and trigger a failing P1/P2 test DAG. Query the
corresponding failure metric, filtered by DAG:

```sql
SELECT latest(`airflow.priority.p1.failed`) FROM Metric FACET dag
```

Create an external alert condition for a positive failure sample, choosing the
evaluation window for your workflow's cadence. See the
[metric reference](API.md#metric-backends) for defaults and state adjustments,
and [troubleshooting](how-to.md#how-to-troubleshoot-missing-alerts) for sender errors.
