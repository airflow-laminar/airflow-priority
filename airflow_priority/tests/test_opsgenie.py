import os

import pytest


@pytest.mark.skipif(os.environ.get("OPSGENIE_API_KEY") is None, reason="Opsgenie api key not set")
def test_opsgenie_send(airflow_config, dag_run):
    from airflow_priority.plugins.opsgenie import send_metric

    send_metric("UNIT TEST", 1, "BEEN TESTED", {})
