from unittest.mock import patch

import pytest


@pytest.mark.parametrize(
    "tag,enabled,count", [("failed", False, 1), ("running", False, 0), ("success", False, 0), ("running", True, 1), ("success", True, 1)]
)
def test_email_state_selection_and_content(tag, enabled, count):
    from airflow_priority.plugins.email import send_metric

    options = {"to": "ops@example.com", "send_running": str(enabled).lower(), "send_success": str(enabled).lower()}

    def config(section, key, **kwargs):
        return options.get(key, kwargs.get("default"))

    with patch("airflow_priority.plugins.email.get_config_option", side_effect=config), patch("airflow_priority.plugins.email.send_email") as send:
        send_metric('dag<&"', 1, tag, {})
    assert send.call_count == count
    if count:
        assert send.call_args.kwargs["to"] == "ops@example.com"
        assert "P1" in send.call_args.kwargs["subject"]
        assert tag in send.call_args.kwargs["subject"]
        assert "&lt;&amp;&quot;" in send.call_args.kwargs["html_content"]


def test_email_registration_requires_recipient():
    from airflow_priority.common import AirflowPriorityConfigurationOptionNotFound
    from airflow_priority.tracker import Tracker

    tracker = Tracker()
    with patch("airflow_priority.tracker.get_config_option", side_effect=AirflowPriorityConfigurationOptionNotFound("email.to")):
        tracker.register("email", [("email", "to")])
    assert "email" not in tracker.backends


def test_email_typed_configuration_is_available():
    from airflow_priority import EmailConfiguration, PriorityConfiguration

    config = PriorityConfiguration(email={"to": "ops@example.com", "threshold": 2})
    assert isinstance(config.email, EmailConfiguration)
    assert config.email.to == "ops@example.com"
    assert config.email.threshold == 2


def test_email_ini_registration_and_threshold_filtering(airflow_config, dag_run):
    from airflow.configuration import conf

    from airflow_priority.common import get_config_option
    from airflow_priority.tracker import Tracker

    conf.add_section("priority.email")
    conf.set("priority.email", "to", "ops@example.com")
    conf.set("priority.email", "threshold", "1")
    get_config_option.cache_clear()
    try:
        tracker = Tracker()
        tracker.register("email", [("email", "to")])
        assert "email" in tracker.backends
        with patch("airflow_priority.plugins.email.send_email") as send:
            tracker.failed(dag_run)
            assert send.call_count == 1
            dag_run.dag.tags = ["P2"]
            tracker.failed(dag_run)
            assert send.call_count == 1
    finally:
        get_config_option.cache_clear()


def test_email_yaml_configuration_registers_backend(airflow_config):
    from pathlib import Path

    from airflow_priority.common import get_config_option
    from airflow_priority.tracker import Tracker

    directory = Path(airflow_config) / "dags" / "config"
    directory.mkdir(parents=True)
    (directory / "config.yaml").write_text(
        "# @package _global_\n_target_: airflow_config.Configuration\nextensions:\n  priority:\n"
        "    _target_: airflow_priority.PriorityConfiguration\n    email:\n"
        "      to: [ops@example.com, backup@example.com]\n      threshold: 2\n      send_running: true\n"
    )
    get_config_option.cache_clear()
    try:
        tracker = Tracker()
        tracker.register("email", [("email", "to")])
        assert tracker.thresholds["email"] == 2
        with patch("airflow_priority.plugins.email.send_email") as send:
            tracker.backends["email"]("test", 1, "running", {})
        assert send.call_args.kwargs["to"] == ["ops@example.com", "backup@example.com"]
    finally:
        get_config_option.cache_clear()
