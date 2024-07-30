from unittest.mock import patch


def test_slack_send(airflow_config, dag_run):
    from airflow_priority.plugins.slack import send_metric_slack

    send_metric_slack("UNIT TEST", 1, "BEEN TESTED")


def test_slack_priority_failed(airflow_config, dag_run):
    from airflow_priority.plugins.slack import on_dag_run_failed

    with patch("airflow_priority.plugins.slack.send_metric_slack") as p1:
        on_dag_run_failed(dag_run, "test")
    assert p1.call_count == 1
