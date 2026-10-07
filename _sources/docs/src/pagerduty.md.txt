# How to create PagerDuty incidents for failed DAGs

Install `airflow-priority[pagerduty]`. Obtain an Events API v2 routing key for an
existing PagerDuty service, then configure the Airflow components:

```ini
[priority.pagerduty]
routing_key = YOUR_EVENTS_ROUTING_KEY
source = airflow.priority
threshold = 2
update = true
```

Use `routing_key`; `api_key` is not the configuration option for this backend.
Restart Airflow components and trigger a failing P1/P2 test DAG. Confirm an
incident is created for its DAG ID and priority.

With `update=true`, later running/success events can acknowledge/resolve the
stored incident for the same DagRun in the same process. To test that path,
change the state of that existing run; a new run has a separate context.
See the [incident reference](API.md#incident-backends) for severity and source
formatting, and the [explanation](explanation.md) for context lifetime.
