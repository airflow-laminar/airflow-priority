# airflow-priority

Route tagged Airflow DAG-run events to alerting and metric backends.

[![Build Status](https://github.com/airflow-laminar/airflow-priority/actions/workflows/build.yaml/badge.svg?branch=main&event=push)](https://github.com/airflow-laminar/airflow-priority/actions/workflows/build.yaml)
[![codecov](https://codecov.io/gh/airflow-laminar/airflow-priority/branch/main/graph/badge.svg)](https://codecov.io/gh/airflow-laminar/airflow-priority)
[![License](https://img.shields.io/github/license/airflow-laminar/airflow-priority)](https://github.com/airflow-laminar/airflow-priority)
[![PyPI](https://img.shields.io/pypi/v/airflow-priority.svg)](https://pypi.python.org/pypi/airflow-priority)

Tag a DAG with P1 through P5 and configure the destinations that should receive
its state changes. Backends apply independent thresholds. The plugin observes
DAG-run running, success, and failure events through Airflow listeners.

## Documentation

- [Tutorial: alert on one failed DAG](docs/src/tutorial.md) sends a tagged failure to a Slack test channel.
- [How-to guides](docs/src/how-to.md) cover priorities, thresholds, environment variables, airflow-config, and delivery troubleshooting.
- [API reference](docs/src/API.md) lists configuration models, backend options, routing, listener hooks, and tracker behavior.
- [Why priority alerts follow DAG-run state](docs/src/explanation.md) explains task callbacks, recovery workflows, and process-local context.

Backend guides cover [Slack](docs/src/slack.md), [Discord](docs/src/discord.md),
[PagerDuty](docs/src/pagerduty.md), [Opsgenie](docs/src/opsgenie.md),
[Symphony](docs/src/symphony.md), [Datadog](docs/src/datadog.md),
[New Relic](docs/src/newrelic.md), [Logfire](docs/src/logfire.md), and
[AWS CloudWatch](docs/src/cloudwatch.md).

Published documentation:
[airflow-laminar.github.io/airflow-priority](https://airflow-laminar.github.io/airflow-priority/).

## Related integrations

[airflow-supervisor](https://github.com/airflow-laminar/airflow-supervisor),
[airflow-nomad](https://github.com/airflow-laminar/airflow-nomad), and
[airflow-cron](https://github.com/airflow-laminar/airflow-cron) produce task logs
and failure diagnostics. Priority routing observes their DAG outcomes;
task callbacks handle task-specific notification needs.

## License

Apache 2.0. See [LICENSE](LICENSE).
