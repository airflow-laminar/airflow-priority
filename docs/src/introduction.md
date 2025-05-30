# Introduction

This repo provides an [Airflow Plugin](https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/plugins.html) for priority-driven DAG failure alerting.
In layman's terms, one need only add a [tag](https://airflow.apache.org/docs/apache-airflow/stable/howto/add-dag-tags.html) to their DAG in `P1, P2, P3, P4, P5`, where `P1` corresponds to highest priority and `P5` corresponds to lowest, and that dag will send a notification to a backend integration.

## Integrations

| Integration                          | Metric / Tag                                                      | Docs |
| :----------------------------------- | :---------------------------------------------------------------- |:-----|
| [Datadog](https://www.datadoghq.com) | `airflow.custom.priority.p{1,2,3,4,5}.{failed,succeeded,running}` | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/datadog.html) |
| [Discord](http://discord.com)        | `N/A`                                                             | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/discord.html) |
| [New Relic](https://newrelic.com)    | `airflow.custom.priority.p{1,2,3,4,5}.{failed,succeeded,running}` | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/newrelic.html) |
| [OpsGenie](https://www.atlassian.com/software/opsgenie) | `N/A`                                          | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/opsgenie.html) |
| [Slack](http://slack.com)            | `N/A`                                                             | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/slack.html) |
| [Symphony](http://symphony.com)      | `N/A`                                                             | [Link](https://airflow-laminar.github.io/airflow-priority/docs/src/symphony.html) |

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
