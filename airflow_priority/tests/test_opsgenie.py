import os
from unittest.mock import MagicMock

import pytest


@pytest.mark.skipif(os.environ.get("OPSGENIE_API_KEY") is None, reason="Opsgenie api key not set")
def test_opsgenie_send(airflow_config, dag_run):
    from airflow_priority.plugins.opsgenie import send_metric

    send_metric("UNIT TEST", 1, "BEEN TESTED", {})


def test_opsgenie_priority_failed(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="opsgenie", necessary_configs=[])
    new_tracker.backends["opsgenie"] = MagicMock()
    new_tracker.failed(dag_run)
    assert new_tracker.backends["opsgenie"].call_count == 1
