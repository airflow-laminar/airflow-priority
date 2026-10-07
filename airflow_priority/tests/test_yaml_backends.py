from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from airflow_priority import get_config_option


@pytest.fixture
def priority_yaml(airflow_config):
    directory = Path(airflow_config) / "dags/config"
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "config.yaml").write_text(
        """# @package _global_
_target_: airflow_config.Configuration
extensions:
  priority:
    _target_: airflow_priority.PriorityConfiguration
    slack:
      token: test-token
      channel: alerts
      send_running: true
      send_success: false
      update_message: true
    datadog:
      api_key: test-key
      tags: [environment:test]
    newrelic:
      api_key: test-key
      tags:
        environment: test
"""
    )
    get_config_option.cache_clear()
    yield
    get_config_option.cache_clear()


def test_yaml_boolean_flags_match_ini_values(priority_yaml):
    assert get_config_option("slack", "send_running") == "true"
    assert get_config_option("slack", "send_success") == "false"
    assert get_config_option("slack", "update_message") == "true"


def test_slack_accepts_yaml_boolean_flags(priority_yaml):
    from airflow_priority.plugins.slack import send_metric

    client = Mock()
    client.chat_postMessage.return_value = {"ts": "message-id"}
    with (
        patch("airflow_priority.plugins.slack.get_client", return_value=client),
        patch("airflow_priority.plugins.slack.get_channel_id", return_value="channel-id"),
    ):
        context = {}
        send_metric("yaml-priority", 3, "running", context)
        send_metric("yaml-priority", 3, "failed", context)
        send_metric("yaml-priority", 3, "success", context)
    assert client.chat_postMessage.call_count == 2
    client.chat_update.assert_called_once()
    assert context == {}


def test_datadog_accepts_yaml_tag_lists(priority_yaml):
    from airflow_priority.plugins.datadog import send_metric

    with patch("airflow_priority.plugins.datadog.ApiClient"), patch("airflow_priority.plugins.datadog.MetricsApi") as metrics:
        metrics.return_value.submit_metrics.return_value = {"errors": []}
        send_metric("yaml-priority", 3, "failed", {})
    tags = metrics.return_value.submit_metrics.call_args.kwargs["body"].series[0].tags
    assert tags == ["application:airflow", "priority:3", "dag:yaml-priority", "environment:test"]


def test_newrelic_accepts_yaml_tag_mappings(priority_yaml):
    from airflow_priority.plugins.newrelic import send_metric

    client = Mock()
    with patch("airflow_priority.plugins.newrelic.get_client", return_value=client):
        send_metric("yaml-priority", 3, "failed", {})
    metric = client.send_batch.call_args.args[0][0]
    assert metric.tags == {"application": "airflow", "priority": "3", "dag": "yaml-priority", "environment": "test"}


def test_datadog_tags_are_optional_in_ini(airflow_config):
    import airflow.configuration

    from airflow_priority.plugins.datadog import send_metric

    airflow.configuration.conf.remove_option("priority.datadog", "tags")
    get_config_option.cache_clear()
    try:
        with patch("airflow_priority.plugins.datadog.ApiClient"), patch("airflow_priority.plugins.datadog.MetricsApi") as metrics:
            metrics.return_value.submit_metrics.return_value = {"errors": []}
            send_metric("ini-priority", 3, "failed", {})
        tags = metrics.return_value.submit_metrics.call_args.kwargs["body"].series[0].tags
        assert tags == ["application:airflow", "priority:3", "dag:ini-priority"]
    finally:
        get_config_option.cache_clear()
