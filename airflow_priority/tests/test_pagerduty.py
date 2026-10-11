from unittest.mock import MagicMock, patch

from airflow_priority.tracker import Tracker


def test_pagerduty(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.pagerduty.get_client") as get_client_mock,
    ):
        mock_client = MagicMock()
        get_client_mock.return_value = mock_client
        mock_client.trigger.return_value = "123"

        from airflow_priority.plugins.pagerduty import send_metric

        # Call the function to test
        send_metric("UNIT TEST", 1, "running", {})
        send_metric("UNIT TEST", 1, "failed", {})
        send_metric("UNIT TEST", 1, "running", {})
        send_metric("UNIT TEST", 1, "success", {})

        assert mock_client.trigger.call_count == 1


def test_pagerduty_sequence(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.pagerduty.get_client") as get_client_mock,
    ):
        mock_client = MagicMock()
        get_client_mock.return_value = mock_client
        mock_client.trigger.return_value = "123"

        tracker = Tracker()
        tracker.register(backend="pagerduty", necessary_configs=[])

        tracker.running(dag_run)
        tracker.failed(dag_run)
        tracker.running(dag_run)
        tracker.success(dag_run)

        assert mock_client.trigger.call_count == 1
        assert mock_client.acknowledge.call_count == 1
        assert mock_client.resolve.call_count == 1


def test_pagerduty_client_uses_routing_key():
    from airflow_priority.plugins.pagerduty import get_client

    get_client.cache_clear()
    try:
        with (
            patch("airflow_priority.plugins.pagerduty.get_config_option", return_value="routing"),
            patch("airflow_priority.plugins.pagerduty.EventsApiV2Client") as client,
        ):
            get_client()
        client.assert_called_once_with(routing_key="routing")
    finally:
        get_client.cache_clear()
