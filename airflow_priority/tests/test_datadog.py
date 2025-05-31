from datetime import datetime
from unittest.mock import MagicMock, call, patch

from datadog_api_client.v2.model.metric_payload import MetricPayload
from datadog_api_client.v2.model.metric_point import MetricPoint
from datadog_api_client.v2.model.metric_resource import MetricResource
from datadog_api_client.v2.model.metric_series import MetricSeries

from airflow_priority.tracker import Tracker


def test_datadog(airflow_config, dag_run):
    now = datetime.now()
    with (
        patch("airflow_priority.plugins.datadog.ApiClient"),
        patch("airflow_priority.plugins.datadog.MetricsApi") as mock_metrics_api,
        patch("airflow_priority.plugins.datadog.datetime") as datetime_mock,
    ):
        datetime_mock.now.return_value = now
        mock_metrics_api.return_value.submit_metrics = MagicMock(return_value={"errors": []})

        from airflow_priority.plugins.datadog import send_metric

        # Call the function to test
        send_metric("UNIT TEST", 1, "testing", {})

        # Assert that the ApiClient was called
        assert mock_metrics_api.return_value.submit_metrics.call_count == 1
        mock_metrics_api.return_value.submit_metrics.assert_called_once_with == call(
            body=MetricPayload(
                series=[
                    MetricSeries(
                        metric="custom.metric.p1.testing",
                        points=[
                            MetricPoint(
                                timestamp=int(now.timestamp()),
                                value=1.0,
                            )
                        ],
                        resources=[MetricResource(name="UNIT TEST", type="dag")],
                        tags=["application:airflow", "priority:1", "dag:UNIT TEST", "environment:test"],
                        type=3,
                    )
                ]
            )
        )


def test_datadog_send_sequence(airflow_config, dag_run):
    now = datetime.now()
    with (
        patch("airflow_priority.plugins.datadog.ApiClient"),
        patch("airflow_priority.plugins.datadog.MetricsApi") as mock_metrics_api,
        patch("airflow_priority.plugins.datadog.datetime") as datetime_mock,
    ):
        datetime_mock.now.return_value = now
        mock_metrics_api.return_value.submit_metrics = MagicMock(return_value={"errors": []})

        tracker = Tracker()
        tracker.register(backend="datadog", necessary_configs=[])

        tracker.running(dag_run)
        tracker.failed(dag_run)
        tracker.running(dag_run)
        tracker.success(dag_run)

        assert mock_metrics_api.return_value.submit_metrics.call_count == 4


def test_datadog_alt(airflow_config_alt, dag_run_p3):
    now = datetime.now()
    with (
        patch("airflow_priority.plugins.datadog.ApiClient"),
        patch("airflow_priority.plugins.datadog.MetricsApi") as mock_metrics_api,
        patch("airflow_priority.plugins.datadog.datetime") as datetime_mock,
    ):
        datetime_mock.now.return_value = now
        mock_metrics_api.return_value.submit_metrics = MagicMock(return_value={"errors": []})

        tracker = Tracker()
        tracker.register(backend="datadog", necessary_configs=[])

        tracker.running(dag_run_p3)
        tracker.failed(dag_run_p3)
        tracker.running(dag_run_p3)
        tracker.success(dag_run_p3)

        assert mock_metrics_api.return_value.submit_metrics.call_count == 0
