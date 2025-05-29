import os
from unittest.mock import MagicMock

import pytest


@pytest.mark.skipif(os.environ.get("SLACK_TOKEN") is None, reason="Slack token token not set")
def test_slack_send(airflow_config, dag_run):
    from airflow_priority.plugins.slack import get_client, send_metric

    get_client.cache_clear()
    send_metric("UNIT TEST", 1, "BEEN TESTED", {})


def test_slack_priority_failed(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="slack", necessary_configs=[])
    new_tracker.backends["slack"] = MagicMock()

    new_tracker.failed(dag_run)
    assert new_tracker.backends["slack"].call_count == 1
