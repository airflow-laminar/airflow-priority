from importlib import import_module
from logging import getLogger
from typing import Dict, List, Tuple

from airflow.models.dagrun import DagRun

from .common import (
    AirflowPriorityConfigurationOptionNotFound,
    BackendSpecificDagContext,
    DagContextIdentifier,
    DagStatus,
    SendMetricFunction,
    get_config_option,
    has_priority_tag,
)

_log = getLogger(__name__)


class Tracker(object):
    def __init__(self):
        self.dagruns: Dict[DagContextIdentifier, Dict[DagStatus, BackendSpecificDagContext]] = {}
        self.backends: Dict[str, SendMetricFunction] = {}
        self.thresholds: Dict[str, int] = {}

    def register(
        self,
        backend: str,
        necessary_configs: List[Tuple[str, str]],
    ):
        if backend in self.backends:
            _log.warning(f"Backend '{backend}' is already registered. Skipping registration.")
            return

        _log.info(f"Registering backend '{backend}' with necessary configs: {necessary_configs}")

        # Ensure all configs are set
        for config in necessary_configs:
            try:
                get_config_option(*config)
            except AirflowPriorityConfigurationOptionNotFound:
                _log.warning(
                    f"Configuration option '{config[0]}.{config[1]}' is not set for backend '{backend}'. Metrics will not be sent for this backend."
                )
                return

        # Import the backend
        try:
            module = import_module(f"airflow_priority.plugins.{backend}")
        except ImportError:
            _log.exception(f"Failed to import plugin for backend '{backend}'. Metrics will not be sent for this backend")
            return

        # register
        self.backends[backend] = getattr(module, "send_metric")

        # set threshold if available
        self.thresholds[backend] = int(get_config_option(backend, "threshold", default=get_config_option("threshold", default=5)))

    def _setup_context(self, backend: str, dag_instance_id: str):
        key = (backend, dag_instance_id)
        if key not in self.dagruns:
            self.dagruns[key] = {}

    def running(self, dag_run: DagRun):
        dag_id, priority = has_priority_tag(dag_run=dag_run)

        if priority:
            _log.info(f"DAG Running: {dag_id} / P{priority}")

            for backend, sender in self.backends.items():
                _log.info(f"Backend: {backend}")

                if priority > self.thresholds.get(backend, 5):
                    _log.info(f"Skipping running metric for backend {backend} with priority {priority} as it exceeds the threshold.")
                    return

                # Setup the context if needed
                self._setup_context(backend, dag_run.id)

                try:
                    sender(dag_id, priority, "running", self.dagruns[(backend, dag_run.id)])
                except Exception:
                    _log.exception(f"Failed to send running metric for DAG {dag_id} with priority {priority} on backend {backend}")

    def success(self, dag_run: DagRun):
        dag_id, priority = has_priority_tag(dag_run=dag_run)

        if priority:
            _log.info(f"DAG Success: {dag_id} / P{priority}")
            for backend, sender in self.backends.items():
                _log.info(f"Backend: {backend}")

                if priority > self.thresholds.get(backend, 5):
                    _log.info(f"Skipping success metric for backend {backend} with priority {priority} as it exceeds the threshold.")
                    return

                # Setup the context if needed
                self._setup_context(backend, dag_run.id)

                try:
                    sender(dag_id, priority, "success", self.dagruns[(backend, dag_run.id)])
                except Exception:
                    _log.exception(f"Failed to send success metric for DAG {dag_id} with priority {priority} on backend {backend}")

    def failed(self, dag_run: DagRun):
        dag_id, priority = has_priority_tag(dag_run=dag_run)
        if priority:
            _log.info(f"DAG Failed: {dag_id} / P{priority}")
            for backend, sender in self.backends.items():
                _log.info(f"Backend: {backend}")

                if priority > self.thresholds.get(backend, 5):
                    _log.info(f"Skipping failed metric for backend {backend} with priority {priority} as it exceeds the threshold.")
                    return

                # Setup the context if needed
                self._setup_context(backend, dag_run.id)

                try:
                    sender(dag_id, priority, "failed", self.dagruns[(backend, dag_run.id)])
                except Exception:
                    _log.exception(f"Failed to send failed metric for DAG {dag_id} with priority {priority} on backend {backend}")


# Single instance of Tracker
tracker_inst = Tracker()


tracker_inst.register(
    backend="aws",
    necessary_configs=[
        ("aws", "region"),
    ],
)


tracker_inst.register(
    backend="datadog",
    necessary_configs=[
        ("datadog", "api_key"),
    ],
)


tracker_inst.register(
    backend="discord",
    necessary_configs=[
        ("discord", "token"),
        ("discord", "channel"),
    ],
)

tracker_inst.register(
    backend="logfire",
    necessary_configs=[
        ("logfire", "token"),
    ],
)

tracker_inst.register(
    backend="newrelic",
    necessary_configs=[
        ("newrelic", "api_key"),
    ],
)

tracker_inst.register(
    backend="opsgenie",
    necessary_configs=[
        ("opsgenie", "api_key"),
    ],
)

tracker_inst.register(
    backend="slack",
    necessary_configs=[
        ("slack", "token"),
        ("slack", "channel"),
    ],
)
tracker_inst.register(
    backend="symphony",
    necessary_configs=[
        ("symphony", "room_name"),
        ("symphony", "message_create_url"),
        ("symphony", "cert_file"),
        ("symphony", "key_file"),
        ("symphony", "session_auth"),
        ("symphony", "key_auth"),
        ("symphony", "room_search_url"),
    ],
)
