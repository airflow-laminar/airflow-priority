import os

import pytest


@pytest.mark.skipif(os.environ.get("SYMPHONY_ROOM_NAME", "") == "", reason="no symphony credentials")
def test_symphony_send(airflow_config, dag_run):
    from airflow_priority.plugins.symphony import send_metric

    send_metric("UNIT TEST", 1, "BEEN TESTED", {})
