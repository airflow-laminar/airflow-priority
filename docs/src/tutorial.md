# Tutorial: alert on one failed DAG

Send a tagged DAG failure to a Slack test channel. Use a working Airflow 3
development instance and a Slack bot already installed in your workspace.
Invite the bot to the test channel. Give it `channels:read`, `groups:read`, and
`chat:write` scopes, as described by Slack's
[channel lookup](https://docs.slack.dev/reference/methods/conversations.list/)
and [message API](https://docs.slack.dev/reference/methods/chat.postMessage/).

## Install the plugin

Activate the environment used by your Airflow components:

```bash
pip install 'airflow-priority[slack]'
```

## Configure the destination

Add this section to the `airflow.cfg` read by the scheduler and API server.
Use your bot's token and channel name, without a leading `#`:

```ini
[priority.slack]
token = YOUR_BOT_TOKEN
channel = airflow-alert-test
threshold = 1
```

Restart those Airflow components after changing configuration. Run:

```bash
airflow plugins
```

The output lists `AirflowPriorityPlugin`.

## Create a failing DAG

Save `priority_demo.py` in your DAG folder:

```python
from datetime import datetime, timezone

from airflow.sdk import DAG, task

with DAG(
    dag_id="priority-demo",
    schedule=None,
    start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
    catchup=False,
    tags=["P1"],
    default_args={"retries": 0},
) as dag:

    @task
    def fail_demo():
        raise RuntimeError("Priority tutorial failure")

    fail_demo()
```

Wait for the DAG to appear in Airflow, then unpause and trigger it:

```bash
airflow dags unpause priority-demo
airflow dags trigger priority-demo
```

The task and DAG run fail. The Slack test channel receives a message saying
that the P1 DAG `priority-demo` was marked `failed`.

## Check the event path

Open the task log to find `Priority tutorial failure`. Open the scheduler log
to find `DAG Failed: priority-demo / P1`. The message is generated from the DAG
run's failure event.

If the DAG fails without a message, follow the
[delivery troubleshooting guide](how-to.md#how-to-troubleshoot-missing-alerts).
The [configuration reference](API.md) lists additional destinations and flags.
