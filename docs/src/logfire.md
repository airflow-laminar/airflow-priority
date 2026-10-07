# How to publish DAG status metrics to Logfire

Install `airflow-priority[logfire]` and obtain a write token for the destination
Logfire project:

```ini
[priority.logfire]
token = YOUR_WRITE_TOKEN
metric = airflow.priority
threshold = 2
```

Restart Airflow components and trigger a failing P1/P2 test DAG. Find the
`airflow.priority.p1.failed` or `airflow.priority.p2.failed` gauge in Logfire.
Configure an external alert on a positive failure sample with a window suited
to the workflow's cadence.

Keep metric names aligned with the configured `metric` prefix. The state
suffix is `success`, not `succeeded`. See the
[metric reference](API.md#metric-backends) for defaults and the limitations of
process-local status adjustments.
