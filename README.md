# airflow-priority

Priority Tags for Airflow Dags

[![Build Status](https://github.com/airflow-laminar/airflow-priority/actions/workflows/build.yml/badge.svg?branch=main&event=push)](https://github.com/airflow-laminar/airflow-priority/actions/workflows/build.yml)
[![codecov](https://codecov.io/gh/airflow-laminar/airflow-priority/branch/main/graph/badge.svg)](https://codecov.io/gh/airflow-laminar/airflow-priority)
[![License](https://img.shields.io/github/license/airflow-laminar/airflow-priority)](https://github.com/airflow-laminar/airflow-priority)
[![PyPI](https://img.shields.io/pypi/v/airflow-priority.svg)](https://pypi.python.org/pypi/airflow-priority)

## Overview

This repo provides an [Airflow Plugin](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/plugins.html) for priority-driven DAG failure alerting.
In layman's terms, one need only add a [tag](https://airflow.apache.org/docs/apache-airflow/stable/howto/add-dag-tags.html) to their DAG in `P1, P2, P3, P4, P5`, where `P1` corresponds to highest priority and `P5` corresponds to lowest, and that dag will send a notification to a backend integration.

[See the documentation for more information on getting started](https://airflow-laminar.github.io/airflow-priority/docs/src/introduction.html)

## Integrations

| Integration                                                                                                                                                                                                        | Metric / Tag                                               | Docs                                                                                |
| :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------- | :---------------------------------------------------------------------------------- |
| <a href="https://www.datadoghq.com"><img width=180 src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/logos/datadog.png" alt="datadog logo"></a>                     | `airflow.priority.p{1,2,3,4,5}.{failed,succeeded,running}` | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/datadog.html)    |
| <a href="http://discord.com"><img width=180 src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/logos/discord.png" alt="discord logo"></a>                            | `N/A`                                                      | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/discord.html)    |
| <a href="https://logfire.pydantic.dev"><img width=180 src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/logos/logfire.png" alt="logfire logo"></a>                  | `airflow.priority.p{1,2,3,4,5}.{failed,succeeded,running}` | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/logfire.html)    |
| <a href="https://pagerduty.com"><img width=180 src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/logos/pagerduty.png" alt="pagerduty logo"></a>                     | `N/A`                                                      | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/pagerduty.html)  |
| <a href="https://newrelic.com"><img width=180 src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/logos/newrelic.png" alt="newrelic logo"></a>                        | `airflow.priority.p{1,2,3,4,5}.{failed,succeeded,running}` | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/newrelic.html)   |
| <a href="https://www.atlassian.com/software/opsgenie"><img width=175 src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/logos/opsgenie.png" alt="opsgenie logo"></a> | `N/A`                                                      | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/opsgenie.html)   |
| <a href="http://slack.com"><img width=175 src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/logos/slack.png" alt="slack logo"></a>                                  | `N/A`                                                      | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/slack.html)      |
| <a href="http://symphony.com"><img width=175 src="https://raw.githubusercontent.com/airflow-laminar/airflow-priority/refs/heads/main/docs/img/logos/symphony.png" alt="symphony logo"></a>                         | `N/A`                                                      | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/symphony.html)   |
| [AWS Cloudwatch](https://aws.amazon.com/cloudwatch/)                                                                                                                                                               | `airflow.priority.p{1,2,3,4,5}.{failed,succeeded,running}` | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/cloudwatch.html) |

## Installation

You can install from pip:

```bash
pip install airflow-priority
```

Or via conda:

```bash
conda install airflow-priority -c conda-forge
```

## License

This software is licensed under the Apache 2.0 license. See the [LICENSE](LICENSE) file for details.
