from unittest.mock import MagicMock, call, patch

from airflow_priority.tracker import Tracker


def test_slack(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.slack.get_client") as get_client_mock,
        patch("airflow_priority.plugins.slack.get_channel_id"),
    ):
        mock_client = MagicMock()
        get_client_mock.return_value = mock_client
        get_client_mock.return_value.chat_postMessage.return_value = {"ts": "1234567890.123456"}

        from airflow_priority.plugins.slack import send_metric

        # Call the function to test
        send_metric("UNIT TEST", 1, "running", {})
        send_metric("UNIT TEST", 1, "failed", {})
        send_metric("UNIT TEST", 1, "running", {})
        send_metric("UNIT TEST", 1, "success", {})

        assert mock_client.chat_postMessage.call_count == 4
        assert mock_client.chat_update.call_count == 0


def test_slack_sequence(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.slack.get_client") as get_client_mock,
        patch("airflow_priority.plugins.slack.get_channel_id") as get_channel_id_mock,
    ):
        mock_client = MagicMock()
        get_client_mock.return_value = mock_client
        get_client_mock.return_value.chat_postMessage.return_value = {"ts": "1234567890.123456"}

        get_channel_id_mock.return_value = 1

        tracker = Tracker()
        tracker.register(backend="slack", necessary_configs=[])

        tracker.running(dag_run)
        tracker.failed(dag_run)
        tracker.running(dag_run)
        tracker.success(dag_run)

        assert mock_client.chat_postMessage.call_count == 4
        assert mock_client.chat_update.call_count == 2
        assert mock_client.chat_update.call_args_list == [
            call(
                channel=1,
                ts="1234567890.123456",
                attachments=[{"mrkdwn_in": ["text"], "color": "#ffff00", "text": 'A P1 DAG "UNIT TEST" has been marked "running"'}],
            ),
            call(
                channel=1,
                ts="1234567890.123456",
                attachments=[{"mrkdwn_in": ["text"], "color": "#00ff00", "text": 'A P1 DAG "UNIT TEST" has been marked "success"'}],
            ),
        ]
