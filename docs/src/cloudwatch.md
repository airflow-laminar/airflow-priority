# How to publish DAG status metrics to CloudWatch

Install `airflow-priority[aws]` in the Airflow environment. Give the process
handling listener events AWS credentials with `cloudwatch:PutMetricData`
permission in the destination account and region.

```ini
[priority.aws]
region = us-east-1
namespace = Airflow/Custom
metric = priority_{tag}
threshold = 2
```

Restart Airflow components and trigger a failing P1/P2 test DAG. In the selected
region, inspect namespace `Airflow/Custom`, metric `priority_failed`, and its
`dag` and `priority` dimensions. Set `AIRFLOW_ENV_NAME` if the `environment`
dimension should identify your deployment instead of `unknown`.

Configure a CloudWatch alarm for the selected failure metric and dimensions.
The initial sample contains the numeric priority; the package does not create
an alarm or SNS destination. This configuration also applies inside MWAA when
its execution role and component configuration provide those permissions.
See the [metric reference](API.md#metric-backends) for the emitted shape.
