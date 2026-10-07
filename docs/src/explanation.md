# Why priority alerts follow DAG-run state

A task can fail while its DAG is still retrying or recovering. Priority tags
classify the workflow, so the plugin listens for DAG-run `running`, `success`,
and `failed` events. That makes a backend notification describe the outcome
of the DAG run rather than every task exception.

Task callbacks serve a different scope. Supervisor, Nomad, and Cron task logs
contain workload output and failure diagnostics. Their callbacks can report
those details directly. The priority listener instead sends the DAG ID, its
priority, and the DAG-run state to configured alerting or metric backends.

## Failure must reach the DAG outcome

A recovery workflow can schedule another run while marking the current run
failed. HA integrations create a failure task after the failed retrigger so
this distinction reaches Airflow. Exhausting recovery attempts keeps an
unhealthy result failed. Time-budget completion is a successful stop, so it
does not itself produce a failure alert.

Airflow decides the DAG outcome from its tasks and trigger rules. An alerting
plugin cannot infer an external workload failure that the DAG reports as
success. A retained service also needs scheduled health checks between its
management runs if outages during that interval must become Airflow events.

## Backend state is local to a process and a DAG run

The tracker stores separate context dictionaries keyed by backend and DagRun
database ID. Slack and incident backends can use that context to update an
earlier failure when the same run changes state in the same process.

The context is not shared between scheduler and API-server processes and is
not persisted through process restarts. A new run, including an HA retrigger,
has an independent context. Update flags do not provide correlation or
automatic resolution across separate DAG runs.

## Thresholds and delivery failures are independent

Each backend applies its own threshold. Filtering one destination leaves
other eligible destinations active. A sender exception is logged and the
tracker continues to the next backend. A lost destination is therefore
separate from the workflow's health, although the tracker offers no durable
queue or delivery retry policy of its own.

Metric backends expose status samples for external monitors. Chat and incident
backends create notifications directly. Metric adjustments and update state
depend on the events a process has observed; they are not a persistent count
of all active or failed workflows.
