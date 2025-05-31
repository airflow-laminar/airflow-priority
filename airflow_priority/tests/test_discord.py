from unittest.mock import MagicMock, call, patch

from airflow_priority.tracker import Tracker


def test_discord(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.discord.get_client") as get_client_mock,
    ):
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_client.inqueue.get.return_value = mock_response
        get_client_mock.return_value = mock_client

        from airflow_priority.plugins.discord import send_metric

        # Call the function to test
        send_metric("UNIT TEST", 1, "running", {})
        send_metric("UNIT TEST", 1, "failed", {})
        send_metric("UNIT TEST", 1, "running", {})
        send_metric("UNIT TEST", 1, "success", {})

        assert mock_client.inqueue.get.call_count == 4
        assert mock_client.outqueue.put.call_count == 4


def test_discord_sequence(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.discord.get_client") as get_client_mock,
    ):
        mock_client = MagicMock()
        mock_client.inqueue.get.return_value = "TEST"
        get_client_mock.return_value = mock_client

        tracker = Tracker()
        tracker.register(backend="discord", necessary_configs=[])

        tracker.running(dag_run)
        tracker.failed(dag_run)
        tracker.running(dag_run)
        tracker.success(dag_run)

        assert mock_client.inqueue.get.call_count == 6
        assert mock_client.outqueue.put.call_count == 6
        assert mock_client.outqueue.put.call_args_list == [
            call((1, 'A P1 DAG "UNIT TEST" has been marked "running"', None, "#ffff00")),
            call((1, 'A P1 DAG "UNIT TEST" has been marked "failed"', None, "#ff0000")),
            call((1, 'A P1 DAG "UNIT TEST" has been marked "running"', None, "#ffff00")),
            call((1, "TEST", 'A P1 DAG "UNIT TEST" has been marked "running"', "#ffff00")),
            call((1, 'A P1 DAG "UNIT TEST" has been marked "success"', None, "#00ff00")),
            call((1, "TEST", 'A P1 DAG "UNIT TEST" has been marked "success"', "#00ff00")),
        ]
