from datetime import UTC, datetime
from importlib import import_module
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

from airflow_priority import format_message, get_run_details
from airflow_priority.tracker import Tracker

RUN_ID = "manual__2025-01-01T00:00:00+00:00"
ENCODED_RUN_ID = "manual__2025-01-01T00%3A00%3A00%2B00%3A00"


@pytest.fixture
def run():
    return SimpleNamespace(
        id=7, dag_id="daily_report", run_id=RUN_ID, logical_date=datetime(2025, 1, 1, tzinfo=UTC), dag=SimpleNamespace(tags=["P1"])
    )


@pytest.mark.parametrize(
    "version,section,suffix", [("2.11.2", "webserver", f"/grid?dag_run_id={ENCODED_RUN_ID}"), ("3.3.2", "api", f"/runs/{ENCODED_RUN_ID}")]
)
def test_run_urls_use_version_specific_base_and_route(run, version, section, suffix):
    with patch("airflow.__version__", version), patch("airflow.configuration.conf.get", return_value="https://airflow.example/prefix/") as get:
        details = get_run_details(run)
    get.assert_called_once_with(section, "base_url", fallback=None)
    assert details == {
        "dag_id": "daily_report",
        "run_id": RUN_ID,
        "logical_date": "2025-01-01T00:00:00+00:00",
        "url": "https://airflow.example/prefix/dags/daily_report" + suffix,
    }


def test_missing_base_url_keeps_run_identifiers(run):
    with patch("airflow.configuration.conf.get", return_value=None):
        details = get_run_details(run)
    assert details["run_id"] == RUN_ID
    assert "url" not in details


def test_missing_run_fields_do_not_create_empty_links(dag_run):
    assert get_run_details(dag_run) == {"dag_id": dag_run.dag_id}


def test_url_matches_native_airflow_task_log_route(airflow_config, run):
    import airflow
    from airflow.configuration import conf

    version3 = int(airflow.__version__.split(".")[0]) >= 3
    section = "api" if version3 else "webserver"
    if not conf.has_section(section):
        conf.add_section(section)
    conf.set(section, "base_url", "https://airflow.example/prefix")
    url = get_run_details(run)["url"]
    if version3:
        RuntimeTaskInstance = import_module("airflow.sdk.execution_time.task_runner").RuntimeTaskInstance
        ti = RuntimeTaskInstance.model_construct(dag_id=run.dag_id, run_id=run.run_id, task_id="run", map_index=-1, try_number=0)
        with patch("airflow.sdk.execution_time.task_runner.conf", conf):
            assert ti.log_url.startswith(url + "/tasks/")
    else:
        from airflow.models.dag import DAG
        from airflow.providers.standard.operators.empty import EmptyOperator

        TaskInstance = import_module("airflow.models.taskinstance").TaskInstance
        DagRun = import_module("airflow.models.dagrun").DagRun
        ti = cast(Any, TaskInstance)(task=EmptyOperator(task_id="run", dag=DAG(dag_id=run.dag_id, schedule=None)), run_id=run.run_id)
        ti.dag_run = cast(Any, DagRun)(dag_id=run.dag_id, run_id=run.run_id, execution_date=run.logical_date)
        with patch("airflow.models.taskinstance.conf", conf):
            assert ti.log_url.split("&task_id=")[0].rstrip("/") == url


@pytest.mark.parametrize("event", ["running", "failed", "success"])
def test_tracker_passes_metadata_to_four_argument_senders(run, event):
    received = []

    def sender(dag_id, priority, tag, context):
        received.append(context["run"].copy())
        context.clear()

    tracker = Tracker()
    tracker.backends["custom"] = sender
    getattr(tracker, event)(run)
    getattr(tracker, event)(run)
    assert [value["run_id"] for value in received] == [RUN_ID, RUN_ID]


def test_messages_escape_html_and_render_clickable_links():
    context = {"run": {"run_id": '<manual&"run>', "logical_date": "2025-01-01", "url": 'https://example/?one=1&two="2"'}}
    text = format_message("test", 1, "failed", context)
    html = format_message("test", 1, "failed", context, html=True)
    assert '<manual&"run>' in text
    assert "&lt;manual&amp;&quot;run&gt;" in html
    assert '<a href="https://example/?one=1&amp;two=&quot;2&quot;">Open DAG run</a>' in html


@pytest.mark.parametrize("backend", ["slack", "discord", "email", "symphony", "pagerduty", "opsgenie"])
def test_notification_payloads_include_run_details(backend):
    module = import_module(f"airflow_priority.plugins.{backend}")
    client = MagicMock()
    client.chat_postMessage.return_value = {"ts": "message"}
    if backend == "opsgenie":
        from opsgenie_sdk import SuccessResponse

        client.create_alert.return_value = SuccessResponse(request_id="request", api_client=client)
    context = {"run": {"run_id": RUN_ID, "logical_date": "2025-01-01T00:00:00+00:00", "url": "https://airflow.example/run"}}
    with patch.object(module, "get_config_option", side_effect=lambda section, key, **kwargs: kwargs.get("default", "ops@example.com")):
        if backend in ("slack", "discord"):
            with patch.object(module, "get_client", return_value=client), patch.object(module, "get_channel_id", return_value="channel"):
                module.send_metric("test", 1, "failed", context)
            payload = str(client.mock_calls)
        elif backend == "email":
            with patch.object(module, "send_email") as send:
                module.send_metric("test", 1, "failed", context)
            payload = str(send.call_args)
        elif backend == "symphony":
            with (
                patch.object(module, "post") as post,
                patch.object(module, "get_config_options", return_value={"message_create_url": "https://example/SID"}),
                patch.object(module, "get_room_id", return_value="room"),
                patch.object(module, "get_headers", return_value={}),
            ):
                module.send_metric("test", 1, "failed", context)
            payload = str(post.call_args)
        else:
            with patch.object(module, "get_client", return_value=client):
                module.send_metric("test", 1, "failed", context)
            payload = str(client.mock_calls)
        assert RUN_ID in payload
        assert "https://airflow.example/run" in payload
