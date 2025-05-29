import os
from unittest.mock import MagicMock

import pytest


@pytest.mark.skipif(os.environ.get("NEWRELIC_API_KEY") is None, reason="New relic token not set")
def test_newrelic_send(airflow_config, dag_run):
    from airflow_priority.plugins.newrelic import send_metric

    send_metric("UNIT TEST", 1, "testing", {})


def test_newrelic_priority_failed(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="newrelic", necessary_configs=[])
    new_tracker.backends["newrelic"] = MagicMock()
    new_tracker.failed(dag_run)
    assert new_tracker.backends["newrelic"].call_count == 1


def test_newrelic_priority_running(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="newrelic", necessary_configs=[])
    new_tracker.backends["newrelic"] = MagicMock()

    new_tracker.backends["newrelic"].reset_mock()
    new_tracker.running(dag_run)
    assert new_tracker.backends["newrelic"].call_count == 1


def test_newrelic_priority_success(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="newrelic", necessary_configs=[])
    new_tracker.backends["newrelic"] = MagicMock()

    new_tracker.backends["newrelic"].reset_mock()
    new_tracker.success(dag_run)
    assert new_tracker.backends["newrelic"].call_count == 1
