---
myst:
  heading_anchors: 3
---

# API reference

`airflow_priority` exports configuration models, priority tags, configuration
lookup, and default metric/source constants. Listener and tracker APIs live in
`airflow_priority.plugin` and `airflow_priority.tracker`.

## Priorities and state events

| Tag | Priority |
| --- | -------- |
| P1  | 1        |
| P2  | 2        |
| P3  | 3        |
| P4  | 4        |
| P5  | 5        |

`has_priority_tag(dag_run)` returns `(dag_id, priority)`; priority is `None`
when no recognized tag is present. Matching is case-insensitive. The first
recognized tag in the DAG's tag iteration order is selected.

`DagStatus` contains `running`, `success`, and `failed`. The plugin's corresponding
DagRun listener functions forward those events to the singleton tracker.
`AirflowPriorityPlugin.listeners` registers the listener module through the
`airflow.plugins` package entry point. This is DAG-run observation, not task
callback registration.

## Configuration lookup

`get_config_option(section, key="", required=True, default=None)` is cached.
Backend options use this precedence:

1. A non-null field on `extensions.priority.<section>` loaded from `$AIRFLOW_HOME/dags/config/config.yaml`.
1. `[priority.<section>]` with option `<key>`, through Airflow's configuration parser.
1. `[priority]` with option `<section>_<key>`.
1. The supplied default.

With an empty key, the INI lookup uses `[priority]` and option `<section>`.
Missing required values raise `AirflowPriorityConfigurationOptionNotFound`.
Configuration-loading errors other than a missing configuration folder can
propagate during plugin initialization.

Typed YAML boolean fields are converted to lowercase `"true"` and `"false"`
strings for backend flag parsing. Datadog tag lists and New Relic tag mappings
remain typed values. Native INI tags use comma-separated strings for Datadog
and JSON-object strings for New Relic.

The global INI threshold defaults to `5`. A backend's explicit threshold
overrides it. `BaseConfiguration.threshold`, inherited by all typed backend
models, defaults to `6`; that model default also takes precedence over the
global INI threshold. Priorities numerically greater than a backend's threshold
are skipped for that backend only.

## Backends

Each configured backend also needs its package extra installed. Registration
requires the options listed below. `PriorityConfiguration` contains optional
fields named `aws`, `datadog`, `discord`, `logfire`, `newrelic`, `opsgenie`,
`pagerduty`, `slack`, and `symphony`; each defaults to `None`.

| Backend        | Extra       | Required registration options                                                                             | Configuration model      |
| -------------- | ----------- | --------------------------------------------------------------------------------------------------------- | ------------------------ |
| AWS CloudWatch | `aws`       | `region`                                                                                                  | `AwsConfiguration`       |
| Datadog        | `datadog`   | `api_key`                                                                                                 | `DataDogConfiguration`   |
| Discord        | `discord`   | `token`, `channel`                                                                                        | `DiscordConfiguration`   |
| Logfire        | `logfire`   | `token`                                                                                                   | `LogfireConfiguration`   |
| New Relic      | `newrelic`  | `api_key`                                                                                                 | `NewRelicConfiguration`  |
| Opsgenie       | `opsgenie`  | `api_key`                                                                                                 | `OpsGenieConfiguration`  |
| PagerDuty      | `pagerduty` | `routing_key`                                                                                             | `PagerDutyConfiguration` |
| Slack          | `slack`     | `token`, `channel`                                                                                        | `SlackConfiguration`     |
| Symphony       | `symphony`  | `room_name`, `message_create_url`, `cert_file`, `key_file`, `session_auth`, `key_auth`, `room_search_url` | `SymphonyConfiguration`  |

### Metric backends

| Backend   | Fields and defaults                                                                            | Output                                                                                                                                                                                          |
| --------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| AWS       | `region`: model default `us-east-1`; `namespace`: `Airflow/Custom`; `metric`: `priority_{tag}` | Metric name substitutes the state for `{tag}`. Dimensions include `environment` from `AIRFLOW_ENV_NAME` or `unknown`, DAG ID, and priority. The initial sample's value is the numeric priority. |
| Datadog   | `host`: `https://api.datadoghq.com`; `metric`: `airflow.priority`; `tags`: model default `[]`  | `<metric>.p<priority>.<state>` gauge samples, with application, DAG, priority, and configured tags.                                                                                             |
| Logfire   | `metric`: `airflow.priority`; optional INI `environment`                                       | `<metric>.p<priority>.<state>` gauges. `environment` is not a field of `LogfireConfiguration`.                                                                                                  |
| New Relic | `metric`: `airflow.priority`; `tags`: model default `{}`                                       | `<metric>.p<priority>.<state>` gauge metrics with application, DAG, priority, and configured tags.                                                                                              |

Metric senders also adjust previously observed states using their context.
These adjustments depend on events seen in that process and do not establish
a durable global count. The state suffix is `success`, not `succeeded`.

### Messaging backends

Slack, Discord, and Symphony expose `send_running`, `send_success`, and
`update_message`, all defaulting to false. Only failures create notifications
by default. Enabling an update uses failure context previously observed for
the same DagRun in the same process.

Slack and Discord colors default to `#ffff00` for running, `#ff0000` for
failed, and `#00ff00` for success. Slack configuration also accepts the
INI-only `nossl` flag, default false, which disables TLS certificate
verification in its client.

Slack `channel` is a channel name without `#`; discovery follows the channel
listing's pagination. Discord `channel` is a numeric channel ID. Routing
overrides, in increasing precedence, are `channel_<state>`, `channel_P<n>`,
and `channel_<state>_P<n>`, above the base `channel`. Symphony uses the same
pattern with `room_name` and matches the selected room name in search results.

Symphony's `message_create_url` replaces `SID` with the selected room ID.
`session_auth` and `key_auth` are certificate-authentication endpoints;
`cert_file` and `key_file` are local certificate/key paths.

### Incident backends

PagerDuty creates a failed-event trigger with its `routing_key` and records
the returned deduplication key. Severity maps P1 through P5 to `critical`,
`error`, `warning`, `info`, and `info`. `source` defaults to `airflow.priority`;
the sender appends `.p<priority>.<state>`.

Opsgenie creates an alert with its `api_key` and records the alert ID. `entity`
defaults to `airflow.priority`, followed by `.p<priority>.<state>`.
Both source/entity values can contain `{priority}` and `{tag}` substitutions.

Both backends' `update` flags default to true. A subsequent running event can
acknowledge the stored incident; success can resolve or close it. This requires
the same DagRun and process context. Independent DAG runs do not share incident
IDs or deduplication keys.

## Tracker

`Tracker.register(backend, necessary_configs)` validates required configuration,
imports `airflow_priority.plugins.<backend>`, registers its `send_metric`
function, and records the threshold. Missing configuration or an unavailable
backend import leaves that backend unregistered.

`running(dag_run)`, `success(dag_run)`, and `failed(dag_run)` dispatch recognized
priority events to each eligible backend. Sender exceptions are logged and do
not stop later backends. There is no tracker-managed delivery queue or retry.

`backends` maps backend names to senders, `thresholds` maps names to integer
limits, and `dagruns` maps `(backend, DagRun.id)` to backend context dictionaries.
The dictionaries are process-local and not persisted. Most senders clear the
context dictionary after success; tracker entries themselves remain in memory.

Each sender has signature
`send_metric(dag_id, priority, tag, context)` and may mutate its context. The
singleton `tracker_inst` attempts to register all supported backends when the
tracker module is imported. Client and configuration caches require process
restart to pick up deployment changes.

## Generated API

```{eval-rst}
.. autosummary::
   :toctree: _build

   airflow_priority.PriorityConfiguration
   airflow_priority.AwsConfiguration
   airflow_priority.DataDogConfiguration
   airflow_priority.DiscordConfiguration
   airflow_priority.LogfireConfiguration
   airflow_priority.NewRelicConfiguration
   airflow_priority.OpsGenieConfiguration
   airflow_priority.PagerDutyConfiguration
   airflow_priority.SlackConfiguration
   airflow_priority.SymphonyConfiguration
   airflow_priority.common
   airflow_priority.plugin
   airflow_priority.tracker.Tracker

```
