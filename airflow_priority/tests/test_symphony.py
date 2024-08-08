import os
from unittest.mock import patch

import pytest


@pytest.mark.skipif(os.environ.get("SYMPHONY_ROOM_NAME", "") == "", reason="no symphony credentials")
def test_symphony_send(airflow_config, dag_run):
    from airflow_priority.plugins.symphony import send_metric_symphony

    send_metric_symphony("UNIT TEST", 1, "BEEN TESTED")


def test_symphony_priority_failed(airflow_config, dag_run):
    from airflow_priority.plugins.symphony import on_dag_run_failed

    with patch("airflow_priority.plugins.symphony.send_metric_symphony") as p1:
        on_dag_run_failed(dag_run, "test")
    assert p1.call_count == 1
