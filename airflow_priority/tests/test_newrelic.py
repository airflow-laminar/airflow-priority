import os
from unittest.mock import patch

import pytest


@pytest.mark.skipif(os.environ.get("NEWRELIC_API_KEY") is None, reason="New relic token not set")
def test_newrelic_send(airflow_config, dag_run):
    from airflow_priority.plugins.newrelic import send_metric_newrelic

    send_metric_newrelic("UNIT TEST", 1, "testing")


def test_newrelic_priority_failed(airflow_config, dag_run):
    from airflow_priority.plugins.newrelic import on_dag_run_failed

    with patch("airflow_priority.plugins.newrelic.send_metric_newrelic") as p1:
        on_dag_run_failed(dag_run, "test")
    assert p1.call_count == 1


def test_newrelic_priority_running(airflow_config, dag_run):
    from airflow_priority.plugins.newrelic import on_dag_run_running

    with patch("airflow_priority.plugins.newrelic.send_metric_newrelic") as p1:
        on_dag_run_running(dag_run, "test")
    assert p1.call_count == 1


def test_newrelic_priority_success(airflow_config, dag_run):
    from airflow_priority.plugins.newrelic import on_dag_run_success

    with patch("airflow_priority.plugins.newrelic.send_metric_newrelic") as p1:
        on_dag_run_success(dag_run, "test")
    assert p1.call_count == 1
