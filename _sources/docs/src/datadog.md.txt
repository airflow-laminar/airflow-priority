# Datadog

<img src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/datadog.png" width=600 alt="Datadog metric for failed DAG run">

Datadog integration will create [Datadog metrics](https://docs.datadoghq.com/metrics/) for DAG `running`, `success`, and `failed` status.

## Setup

Create a new Datadog api key [following their guide](https://docs.datadoghq.com/account_management/api-app-keys/#add-an-api-key-or-client-token).

## Configuration

- `api_key`: (**Required**) the API Key from above
- `host`: (Optional) Override the Datadog API host name. This is necessary for certain US and EU customers to use the Datadog API. The default is `https://api.datadoghq.com`
- `metric`: (Optional) Override the name of the metric. The default is `airflow.priority`, which will product metrics like `airflow.priority.p1.failed`
- `tags`: (Optional) Optional extra tags to include, should be a comma separated list of `key:value` strings, e.g. `tag1:val1,tag2:val2`
- `threshold`: (Optional) Maximum alert threshold. Alerts with higher numerical priority (lower logical priority) will be ignored

## Example

```
[priority.datadog]
api_key = the api key
host = https://us1.datadoghq.com
metric = my.custom.metric  # will produce metrics like my.custom.metric.p2.success
threshold = 2  # only P1 and P2
```

## Monitor

Under `Monitors`, you can create a custom Datadog monitor to generate alerts when your DAGs fail.

To do so, follow the steps below.
Note that some choices can be varied depending on your desired response time.

- Create a `New Monitor` and then choose `Metric`
- Use the default `Threshold Alert`
- Choose the correct metric source (the default would be something like `airflow.priority.p1.failed`, but might vary if you customize the metric name)
- Select `from (everywhere)`, then `min by dag`
- Evaluate `sum` over the `last 5 minutes`
- Set `Alert Threshold > 0`, `Warning threshold > -1`, which alert as soon as a DAG fails
