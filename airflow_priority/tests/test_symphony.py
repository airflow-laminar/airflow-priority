import os
from unittest.mock import MagicMock

import pytest


@pytest.mark.skipif(os.environ.get("SYMPHONY_ROOM_NAME", "") == "", reason="no symphony credentials")
def test_symphony_send(airflow_config, dag_run):
    from airflow_priority.plugins.symphony import send_metric

    send_metric("UNIT TEST", 1, "BEEN TESTED", {})


@pytest.mark.skipif(os.environ.get("SYMPHONY_ROOM_NAME", "") == "", reason="no symphony credentials")
def test_symphony_priority_failed(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="symphony", necessary_configs=[])

    new_tracker.backends["symphony"] = MagicMock()
    new_tracker.failed(dag_run)
    assert new_tracker.backends["symphony"].call_count == 1
