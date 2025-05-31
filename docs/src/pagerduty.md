# Pagerduty

<img src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/pagerduty.png" width=600 alt="Pagerduty alert showing failed DAG status">

Pagerduty integration will create [Pagerduty Alerts](https://support.pagerduty.com/main/docs/alerts) when a DAG fails.

## Setup

Under `Integrations` -> `API Access Keys`, create a new `API` key.
This will generate an api key.

## Configuration

- `api_key`: (**Required**) the API Key from above
- `source`: (Optional) Override the name of the source. The default is `airflow.priority`, which will product alerts with entity like `airflow.priority.p1.failed`
- `update`: (Optional) Update an open alert when DAG is rerun or passes (default is `true`). When `true`, when the DAG is `running` again the alert will be ack'd. If the DAG succeeds, the alert will be resolved.
- `threshold`: (Optional) Maximum alert threshold. Alerts with higher numerical priority (lower logical priority) will be ignored

## Example

```
[priority.pagerduty]
api_key = ...
source = my.entity
update = true
threshold = 2  # only P1 and P2
```
