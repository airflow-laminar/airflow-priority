from unittest.mock import MagicMock, patch

from airflow_priority.tracker import Tracker


def test_logfire(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.logfire.get_gauges") as mock_gauges,
    ):
        mock_gauges.return_value = {("testing", 1): MagicMock()}

        from airflow_priority.plugins.logfire import send_metric

        # Call the function to test
        send_metric("UNIT TEST", 1, "testing", {})

        assert mock_gauges.return_value[("testing", 1)].set.call_count == 1


def test_logfire_sequence(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.logfire.get_gauges") as mock_gauges,
    ):
        mock_gauges.return_value = {
            ("running", 1): MagicMock(),
            ("success", 1): MagicMock(),
            ("failed", 1): MagicMock(),
        }

        tracker = Tracker()
        tracker.register(backend="logfire", necessary_configs=[])

        tracker.running(dag_run)
        tracker.failed(dag_run)
        tracker.running(dag_run)
        tracker.success(dag_run)

        assert mock_gauges.return_value[("running", 1)].set.call_count == 4
        assert mock_gauges.return_value[("failed", 1)].set.call_count == 2
        assert mock_gauges.return_value[("success", 1)].set.call_count == 1
