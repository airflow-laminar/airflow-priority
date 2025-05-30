import os

import pytest


@pytest.mark.skipif(os.environ.get("SLACK_TOKEN") is None, reason="Slack token token not set")
def test_slack_send(airflow_config, dag_run):
    from airflow_priority.plugins.slack import get_client, send_metric

    get_client.cache_clear()
    send_metric("UNIT TEST", 1, "BEEN TESTED", {})
