import os
from unittest.mock import MagicMock

import pytest


@pytest.mark.skipif(os.environ.get("DISCORD_TOKEN") is None, reason="Discord token not set")
def test_discord_send(airflow_config, dag_run):
    from airflow_priority.plugins.discord import send_metric

    send_metric("UNIT TEST", 1, "BEEN TESTED", {})


def test_discord_priority_failed(airflow_config, dag_run, new_tracker):
    new_tracker.register(backend="discord", necessary_configs=[])
    new_tracker.backends["discord"] = MagicMock()
    new_tracker.failed(dag_run)
    assert new_tracker.backends["discord"].call_count == 1
