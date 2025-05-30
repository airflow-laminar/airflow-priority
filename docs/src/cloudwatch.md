# AWS MWAA CloudWatch

To use with [AWS MWAA](https://aws.amazon.com/managed-workflows-for-apache-airflow/), set the AWS region to match your MWAA instance.

```
[priority.aws]
region = "us-east-1"
```

## Alternative Syntax

> [!NOTE]
> AWS MWAA may require you to use the alternative configuration syntax

All scoped configuration options can be set directly under `priority`.

For example this:

```
[priority.aws]
region = "us-east-1"
```

Can be provided as:

```
[priority]
aws_region = "us-east-1"
```
