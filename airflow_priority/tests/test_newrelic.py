from unittest.mock import MagicMock, patch

from airflow_priority.tracker import Tracker


def test_newrelic(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.newrelic.MetricClient") as mock_metric_client,
    ):
        mock_client = MagicMock()
        mock_metric_client.return_value = mock_client

        from airflow_priority.plugins.newrelic import send_metric

        # Call the function to test
        send_metric("UNIT TEST", 1, "testing", {})

        assert mock_client.send_batch.call_count == 1
        assert mock_client.send_batch.call_args_list[0][0][0][0].name == "custom.metric.p1.testing"
        assert mock_client.send_batch.call_args_list[0][0][0][0].tags == {
            "application": "airflow",
            "priority": "1",
            "dag": "UNIT TEST",
            "environment": "test",
        }


def test_newrelic_sequence(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.newrelic.MetricClient") as mock_metric_client,
    ):
        from airflow_priority.plugins.newrelic import get_client

        get_client.cache_clear()
        mock_client = MagicMock()
        mock_metric_client.return_value = mock_client

        tracker = Tracker()
        tracker.register(backend="newrelic", necessary_configs=[])

        tracker.running(dag_run)
        tracker.failed(dag_run)
        tracker.running(dag_run)
        tracker.success(dag_run)

        assert mock_client.send_batch.call_count == 4
        assert mock_client.send_batch.call_args_list[0][0][0][0].name == "custom.metric.p1.running"
        assert mock_client.send_batch.call_args_list[1][0][0][0].name == "custom.metric.p1.failed"
        assert mock_client.send_batch.call_args_list[2][0][0][0].name == "custom.metric.p1.running"
        assert mock_client.send_batch.call_args_list[3][0][0][0].name == "custom.metric.p1.success"
