# How to alert an existing Opsgenie integration

This guide applies to existing Opsgenie deployments. Atlassian ended new sales
on June 4, 2025 and schedules end of support for April 5, 2027; consult its
[migration guidance](https://support.atlassian.com/opsgenie/docs/choose-the-right-path-and-schedule-migration/)
when planning deployment changes.

Install `airflow-priority[opsgenie]` and provide an API key for the existing
integration:

```ini
[priority.opsgenie]
api_key = YOUR_INTEGRATION_KEY
entity = airflow.priority
threshold = 2
update = true
```

Restart Airflow components and trigger a failing P1/P2 test DAG. Confirm the
created alert contains its DAG ID and priority. Sender logs report failed
create, acknowledge, close, or request-status operations.

Same-run running and success events can acknowledge and close the stored alert
when its context remains in that process. See the
[incident reference](API.md#incident-backends) for update semantics and
[troubleshooting](how-to.md#how-to-troubleshoot-missing-alerts) for missing delivery.
