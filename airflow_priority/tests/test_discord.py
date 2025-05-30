import os

import pytest


@pytest.mark.skipif(os.environ.get("DISCORD_TOKEN") is None, reason="Discord token not set")
def test_discord_send(airflow_config, dag_run):
    from airflow_priority.plugins.discord import send_metric

    send_metric("UNIT TEST", 1, "BEEN TESTED", {})
