import os
from unittest.mock import MagicMock

import pytest


@pytest.mark.skipif(os.environ.get("DATADOG_API_KEY") is None, reason="Datadog key not set")
def test_datadog_send(airflow_config, dag_run):
    from airflow_priority.plugins.datadog import send_metric

    send_metric("UNIT TEST", 1, "testing", {})


@pytest.mark.skipif(os.environ.get("DATADOG_API_KEY") is None, reason="Datadog key not set")
def test_datadog_send_alt(airflow_config_alt, dag_run):
    from airflow_priority.plugins.datadog import send_metric

    send_metric("UNIT TEST", 1, "testing", {})


def test_datadog_priority_failed(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="datadog", necessary_configs=[])
    new_tracker.backends["datadog"] = MagicMock()

    new_tracker.failed(dag_run)
    assert new_tracker.backends["datadog"].call_count == 1


def test_datadog_priority_running(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="datadog", necessary_configs=[])
    new_tracker.backends["datadog"] = MagicMock()
    new_tracker.running(dag_run)
    assert new_tracker.backends["datadog"].call_count == 1


def test_datadog_priority_success(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="datadog", necessary_configs=[])
    new_tracker.backends["datadog"] = MagicMock()
    new_tracker.success(dag_run)
    assert new_tracker.backends["datadog"].call_count == 1


def test_datadog_threshold(airflow_config, dag_run_p3, new_tracker):
    new_tracker.register(backend="datadog", necessary_configs=[])
    new_tracker.backends["datadog"] = MagicMock()
    new_tracker.success(dag_run_p3)
    assert new_tracker.backends["datadog"].call_count == 0


def test_datadog_threshold_alt(airflow_config_alt, dag_run_p3, new_tracker):
    new_tracker.register(backend="datadog", necessary_configs=[])
    new_tracker.backends["datadog"] = MagicMock()
    new_tracker.success(dag_run_p3)
    assert new_tracker.backends["datadog"].call_count == 0
