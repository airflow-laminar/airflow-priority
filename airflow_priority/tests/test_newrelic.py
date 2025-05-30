import os

import pytest


@pytest.mark.skipif(os.environ.get("NEWRELIC_API_KEY") is None, reason="New relic token not set")
def test_newrelic_send(airflow_config, dag_run):
    from airflow_priority.plugins.newrelic import send_metric

    send_metric("UNIT TEST", 1, "testing", {})
