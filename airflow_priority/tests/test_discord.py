import os
from unittest.mock import patch

import pytest


@pytest.mark.skipif(os.environ.get("DISCORD_TOKEN") is None, reason="Discord token not set")
def test_discord_send(airflow_config, dag_run):
    from airflow_priority.plugins.discord import send_metric_discord

    send_metric_discord("UNIT TEST", 1, "BEEN TESTED")


def test_discord_priority_failed(airflow_config, dag_run):
    from airflow_priority.plugins.discord import on_dag_run_failed

    with patch("airflow_priority.plugins.discord.send_metric_discord") as p1:
        on_dag_run_failed(dag_run, "test")
    assert p1.call_count == 1
