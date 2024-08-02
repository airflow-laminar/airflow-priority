# airflow-priority

Priority Tags for Airflow Dags

[![Build Status](https://github.com/airflow-laminar/airflow-priority/actions/workflows/build.yml/badge.svg?branch=main&event=push)](https://github.com/airflow-laminar/airflow-priority/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/airflow-laminar/airflow-priority/branch/main/graph/badge.svg)](https://codecov.io/gh/airflow-laminar/airflow-priority)
[![License](https://img.shields.io/github/license/airflow-laminar/airflow-priority)](https://github.com/airflow-laminar/airflow-priority)
[![PyPI](https://img.shields.io/pypi/v/airflow-priority.svg)](https://pypi.python.org/pypi/airflow-priority)

## Overview

This repo provides [Airflow Plugins](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/plugins.html) for priority-driven DAG failure alerting. In layman's terms, one need only add a [tag](https://airflow.apache.org/docs/apache-airflow/stable/howto/add-dag-tags.html) to their DAG in `P1, P2, P3, P4, P5`, and that dag will send a notification to:

- [New Relic](https://newrelic.com)
- [Datadog](https://www.datadoghq.com)
- [Slack](http://slack.com)

Where `P1` corresponds to highest priority, and `P5` corresponds to lowest.

## Installation

You can install from pip:

```bash
pip install airflow-priority
```

Or via conda:

```bash
conda install airflow-priority -c conda-forge
```

## Integrations
| Integration | Metric / Tag |
| :---------- | :----------- |
| [New Relic](https://newrelic.com) | `airflow.custom.priority.p{1,2,3,4,5}.{failed,succeeded,running}` |
| [Datadog](https://www.datadoghq.com) | `airflow.custom.priority.p{1,2,3,4,5}.{failed,succeeded,running}` |
| [Slack](http://slack.com) | `N/A` | 


### New Relic

Create a new New Relic API Key [following their guide](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/). Note that the type should have `INGEST - LICENSE`.

Copy this api key into your `airflow.cfg` like so:

```
[priority.newrelic]
api_key = the api key
```

Under `Query Your Data` in the New Relic UI, you can create a query for the new custom metric:

```
SELECT sum(`airflow.custom.priority.p1.failed`) FROM Metric FACET dag
```

With this, you can now [create a custom alert](https://docs.newrelic.com/docs/alerts/create-alert/examples/define-custom-metrics-alert-condition/). For fast alerting, we recommend the following parameters:

```raw
Window duration - 30 seconds
Sliding window aggregation - Disabled
Slide by interval - Not set
Streaming method - Event timer
Timer - 5 seconds

Fill data gaps with - None
Evaluation delay - Not set

Thresholds: Critical: Query result is above or equals 1 at least once in 1 minute
```

### Slack

Configure a new slack application following the [Slack Quickstart](https://api.slack.com/quickstart).

Ensure your application has the following scopes for public and private channel access:

- `channels:read`
- `groups:read`
- `chat:write`

Enable and install your Slack application into your workspace, and add it as an integration in whatever channel you want it to post.

Copy your Slack application's Oauth Token (starting with `xoxb-`) and your desired channel into your `airflow.cfg` like so:

```
[priority.slack]
token = xoxb-...
channel = channel-name
```

### Datadog

Create a new Datadog api key [following their guide](https://docs.datadoghq.com/account_management/api-app-keys/#add-an-api-key-or-client-token).

Copy this api key into your `airflow.cfg` like so:

```
[priority.datadog]
api_key = the api key
```

Ensure your dags are configured with tags and run some, it can often be convenient to have an intentionally failing `P1` dag to test the integration. With this, you can now [create custom monitors](https://docs.datadoghq.com/getting_started/monitors/) for the tags.


## License
