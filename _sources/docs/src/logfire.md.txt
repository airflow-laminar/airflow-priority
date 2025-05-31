# Logfire

<img src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/logfire.png" width=600 alt="Logfire metric for failed DAG run">

Logfire integration will create [Logfire metrics](https://logfire.pydantic.dev/docs/guides/onboarding-checklist/add-metrics/#gauge-callback) for DAG `running`, `success`, and `failed` status.

## Setup

Create a new Logfire token [following their guide](https://logfire.pydantic.dev/docs/how-to-guides/create-write-tokens/).

## Configuration

- `token`: (**Required**) the token from above
- `metric`: (Optional) Override the name of the metric. The default is `airflow.priority`, which will product metrics like `airflow.priority.p1.failed`
- `threshold`: (Optional) Maximum alert threshold. Alerts with higher numerical priority (lower logical priority) will be ignored

## Example

```
[priority.logfire]
token = the token
metric = my.custom.metric  # will produce metrics like my.custom.metric.p2.success
threshold = 2  # only P1 and P2
```

## Alerts

Under `Alerts`, you can create a custom Logfire alert to generate alerts when your DAGs fail.

To do so, follow the steps below.
Note that some choices can be varied depending on your desired response time.

- Create a `New Alert`
- Use the following SQL Query: `select * from metrics where "metric_name" = 'airflow.priority.p1.failed' and "scalar_value" = 1`
- Adjust the notification parameters as needed, use `Notify me when` `the query has any results`
- See Slack for information about creating a slack alert, you can use Slack webhooks

## Utilities

Here is an example of querying all failed metrics in Logfire, which might be useful for debugging connectivity issues/

```
select * from metrics where "metric_name" = 'airflow.priority.p1.failed'
```
