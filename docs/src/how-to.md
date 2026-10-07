---
myst:
  heading_anchors: 3
---

# How-to guides

Configure priority routing and connect it to existing Airflow workflows.
For a first Slack alert, use the [tutorial](tutorial.md).

## How to select a priority and threshold

Add one priority tag to the DAG. `P1` is highest urgency and `P5` is lowest:

```python
from datetime import datetime, timezone

from airflow import DAG

dag = DAG(
    dag_id="production-report",
    schedule="@daily",
    start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["P2"],
)
```

Install the integration extra for each configured backend in the Airflow
environment. Set a global threshold in `airflow.cfg`, then override it for
individual backends:

```ini
[priority]
threshold = 3

[priority.slack]
token = YOUR_BOT_TOKEN
channel = airflow-alerts
threshold = 2

[priority.datadog]
api_key = YOUR_API_KEY
threshold = 3
```

This routes P1/P2 events to both backends and P3 events only to Datadog.
A threshold filters only its own backend. Choose destinations in the
[backend reference](API.md#backends).

## How to inject configuration through environment variables

Use Airflow's flat configuration section for deployment systems that cannot
set environment-variable names containing dots:

```bash
export AIRFLOW__PRIORITY__SLACK_CHANNEL=airflow-alerts
export AIRFLOW__PRIORITY__SLACK_THRESHOLD=2
```

Inject `AIRFLOW__PRIORITY__SLACK_TOKEN` from your deployment's secret store.
An equivalent flat INI configuration is:

```ini
[priority]
slack_token = YOUR_BOT_TOKEN
slack_channel = airflow-alerts
slack_threshold = 2
```

Configure all processes that receive events, including the scheduler and
Airflow 3 API server. Restart them after changes; configuration and clients
are cached per process. See Airflow's
[configuration guide](https://airflow.apache.org/docs/apache-airflow/stable/howto/set-config.html)
for its environment-variable and secret-backend rules.

## How to configure routing with airflow-config

Install the config extra alongside the backend extra:

```bash
pip install 'airflow-priority[config,slack]'
```

Save `config.yaml` at `$AIRFLOW_HOME/dags/config/config.yaml`:

```yaml
# @package _global_
_target_: airflow_config.Configuration
_convert_: all

extensions:
  priority:
    _target_: airflow_priority.PriorityConfiguration
    slack:
      token: ${oc.env:PRIORITY_SLACK_TOKEN}
      channel: airflow-alerts
      threshold: 2
      send_running: false
      send_success: false
      update_message: false
```

Provide `PRIORITY_SLACK_TOKEN` to the scheduler and API server, then restart
them. This configuration is loaded automatically by the priority plugin; it
does not need a separate DAG loader. The lookup uses this location even when
Airflow's DAG folder is configured elsewhere.

Set the tag in an existing airflow-config DAG definition:

```yaml
dags:
  production-report:
    schedule: "@daily"
    start_date: "2025-01-01"
    catchup: false
    tags: [P2]
    tasks:
      run:
        _target_: airflow_pydantic.BashTask
        bash_command: /opt/jobs/report
```

Materialize that DAG using your existing airflow-config loader. Backend
configuration and DAG definitions may live in the same configuration file.
Use native YAML booleans for notification flags, lists for Datadog tags, and
mappings for New Relic tags. See the [reference](API.md#configuration-lookup)
for precedence and model defaults.

## How to alert on Supervisor, Nomad, and Cron failures

Apply a priority tag to the generated or parent DAG. A failed DAG run can then
reach the configured priority backends:

```yaml
tags: [P1]
```

Keep Supervisor or Nomad `forward_logs: true` when workload output is needed
in task logs. Their failure branches and HA retrigger exhaustion report failed
DAG runs. Cron conversion uses ordinary Bash tasks; preserve a failing exit
status and set `skip_on_exit_code: null` if exit 99 must also fail.

Use task failure callbacks when you need a notification for a specific task
or its process diagnostics. Priority listeners observe DAG-run state and send
the DAG ID, priority, and state. They do not forward workload stdout/stderr or
include task exception traces in backend messages.

## How to troubleshoot missing alerts

Check these conditions in order:

1. Confirm the installed backend extra and `AirflowPriorityPlugin` in `airflow plugins`.
1. Inspect startup logs for backend registration and missing required options.
1. Confirm one recognized priority tag and an inclusive backend threshold.
1. Confirm the DAG run reached `failed`; a failed task alone may not establish that state.
1. Inspect the Airflow process handling the event for `Failed to send` exceptions.
1. Check the destination's credentials, routing key or channel, and permissions.

Unconfigured optional backends log registration warnings. Diagnose the backend
you intend to use. Sender errors are logged and processing continues to other
eligible backends; delivery is not queued for retry by the tracker.

Airflow 3 UI/API state changes also emit DAG success/failure listener events.
Use a test DAG and destination when manually changing state. See the
[listener documentation](https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/listeners.html).
