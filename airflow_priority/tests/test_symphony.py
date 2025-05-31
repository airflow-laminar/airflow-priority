from unittest.mock import patch


def test_symphony_send(airflow_config, dag_run):
    with (
        patch("airflow_priority.plugins.symphony.post") as post_mock,
        patch("airflow_priority.plugins.symphony.get_headers") as get_headers_mock,
        patch("airflow_priority.plugins.symphony.get_room_id") as get_room_id_mock,
    ):
        get_room_id_mock.return_value = ""
        from airflow_priority.plugins.symphony import send_metric

        send_metric("UNIT TEST", 1, "failed", {})

        assert post_mock.call_count == 1
        assert get_headers_mock.call_count == 1
