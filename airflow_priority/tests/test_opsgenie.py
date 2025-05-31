from unittest.mock import MagicMock, patch

from opsgenie_sdk import (
    SuccessResponse,
)

from airflow_priority.tracker import Tracker


def test_opsgenie(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.opsgenie.get_client") as get_client_mock,
    ):
        mock_client = MagicMock()
        get_client_mock.return_value = mock_client
        mock_client.get_request_status.return_value = MagicMock(data=MagicMock(alert_id="alert-1234567890"))
        mock_client.create_alert.return_value = SuccessResponse(request_id="request-1234567890", api_client=mock_client)

        from airflow_priority.plugins.opsgenie import send_metric

        # Call the function to test
        send_metric("UNIT TEST", 1, "running", {})
        send_metric("UNIT TEST", 1, "failed", {})
        send_metric("UNIT TEST", 1, "running", {})
        send_metric("UNIT TEST", 1, "success", {})

        assert mock_client.create_alert.call_count == 1
        assert mock_client.get_request_status.call_count == 1


def test_opsgenie_sequence(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.opsgenie.get_client") as get_client_mock,
    ):
        mock_client = MagicMock()
        get_client_mock.return_value = mock_client
        mock_client.get_request_status.return_value = MagicMock(data=MagicMock(alert_id="alert-1234567890"))
        mock_client.create_alert.return_value = SuccessResponse(request_id="request-1234567890", api_client=mock_client)
        mock_client.acknowledge_alert.return_value = SuccessResponse(request_id="request-1234567890", api_client=mock_client)
        mock_client.close_alert.return_value = SuccessResponse(request_id="request-1234567890", api_client=mock_client)

        tracker = Tracker()
        tracker.register(backend="opsgenie", necessary_configs=[])

        tracker.running(dag_run)
        tracker.failed(dag_run)
        tracker.running(dag_run)
        tracker.success(dag_run)

        assert mock_client.get_request_status.call_count == 3
        assert mock_client.create_alert.call_count == 1
        assert mock_client.acknowledge_alert.call_count == 1
        assert mock_client.close_alert.call_count == 1


#         assert mock_client.chat_postMessage.call_count == 4
#         assert mock_client.chat_update.call_count == 2
#         assert mock_client.chat_update.call_args_list == [
#             call(
#                 channel=1,
#                 ts="1234567890.123456",
#                 attachments=[{"mrkdwn_in": ["text"], "color": "#ffff00", "text": 'A P1 DAG "UNIT TEST" has been marked "running"'}],
#             ),
#             call(
#                 channel=1,
#                 ts="1234567890.123456",
#                 attachments=[{"mrkdwn_in": ["text"], "color": "#00ff00", "text": 'A P1 DAG "UNIT TEST" has been marked "success"'}],
#             ),
#         ]
