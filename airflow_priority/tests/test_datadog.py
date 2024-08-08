import os
from unittest.mock import patch

import pytest


@pytest.mark.skipif(os.environ.get("DATADOG_API_KEY") is None, reason="Datadog key not set")
def test_datadog_send(airflow_config, dag_run):
    from airflow_priority.plugins.datadog import send_metric_datadog

    send_metric_datadog("UNIT TEST", 1, "testing")


def test_datadog_priority_failed(airflow_config, dag_run):
    from airflow_priority.plugins.datadog import on_dag_run_failed

    with patch("airflow_priority.plugins.datadog.send_metric_datadog") as p1:
        on_dag_run_failed(dag_run, "test")
    assert p1.call_count == 1


def test_datadog_priority_running(airflow_config, dag_run):
    from airflow_priority.plugins.datadog import on_dag_run_running

    with patch("airflow_priority.plugins.datadog.send_metric_datadog") as p1:
        on_dag_run_running(dag_run, "test")
    assert p1.call_count == 1


def test_datadog_priority_success(airflow_config, dag_run):
    from airflow_priority.plugins.datadog import on_dag_run_success

    with patch("airflow_priority.plugins.datadog.send_metric_datadog") as p1:
        on_dag_run_success(dag_run, "test")
    assert p1.call_count == 1
