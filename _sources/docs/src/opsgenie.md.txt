# OpsGenie

<img src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/opsgenie.png" width=600 alt="OpsGenie alert showing failed DAG status">

OpsGenie integration will create [OpsGenie Alerts](https://docs.opsgenie.com/docs/alert-api) when a DAG fails.

## Setup

Under `Teams` -> `<your team>` -> `Integrations`, add a new `API` integration.
This will generate an api key.

## Configuration

- `api_key`: (**Required**) the API Key from above
- `entity`: (Optional) Override the name of the entity. The default is `airflow.priority`, which will product alerts with entity like `airflow.priority.p1.failed`
- `update`: (Optional) Update an open alert when DAG is rerun or passes (default is `true`). When `true`, when the DAG is `running` again the alert will be ack'd. If the DAG succeeds, the alert will be closed.
- `threshold`: (Optional) Maximum alert threshold. Alerts with higher numerical priority (lower logical priority) will be ignored

## Example

```
[priority.opsgenie]
api_key = ...
entity = my.entity
update = true
threshold = 2  # only P1 and P2
```
