from types import SimpleNamespace
from unittest.mock import Mock, call, patch

import pytest


def test_slack_channel_discovery_follows_pagination():
    from airflow_priority.plugins.slack import get_channel_id

    client = Mock()
    client.conversations_list.side_effect = [
        SimpleNamespace(data={"ok": True, "channels": [], "response_metadata": {"next_cursor": "next-page"}}),
        SimpleNamespace(data={"ok": True, "channels": [{"name": "alerts", "id": "channel-id"}], "response_metadata": {"next_cursor": ""}}),
    ]
    get_channel_id.cache_clear()
    try:
        with (
            patch("airflow_priority.plugins.slack.get_client", return_value=client),
            patch("airflow_priority.plugins.slack.get_config_option", return_value="alerts"),
        ):
            assert get_channel_id("failed", 3) == "channel-id"
    finally:
        get_channel_id.cache_clear()
    assert client.conversations_list.call_args_list == [
        call(types=["public_channel", "private_channel"], cursor=None),
        call(types=["public_channel", "private_channel"], cursor="next-page"),
    ]


def test_slack_missing_channel_raises_after_last_page():
    from airflow_priority.plugins.slack import get_channel_id

    client = Mock()
    client.conversations_list.return_value = SimpleNamespace(data={"ok": True, "channels": []})
    get_channel_id.cache_clear()
    try:
        with (
            patch("airflow_priority.plugins.slack.get_client", return_value=client),
            patch("airflow_priority.plugins.slack.get_config_option", return_value="alerts"),
            pytest.raises(RuntimeError, match="Slack channel not found: alerts"),
        ):
            get_channel_id("failed", 3)
    finally:
        get_channel_id.cache_clear()
    client.conversations_list.assert_called_once()


def test_symphony_search_matches_priority_room_override():
    from airflow_priority.plugins.symphony import get_room_id

    response = Mock(status_code=200)
    response.json.return_value = {"rooms": [{"roomAttributes": {"name": "priority-room"}, "roomSystemInfo": {"id": "room-id"}}]}
    options = {"room_search_url": "https://symphony.example.test/search"}

    def config(section, key, **kwargs):
        return "priority-room" if key == "room_name_failed_P1" else kwargs.get("default", "")

    get_room_id.cache_clear()
    try:
        with (
            patch("airflow_priority.plugins.symphony.get_config_options", return_value=options),
            patch("airflow_priority.plugins.symphony.get_config_option", side_effect=config),
            patch("airflow_priority.plugins.symphony.get_headers", return_value={}),
            patch("airflow_priority.plugins.symphony.post", return_value=response) as post,
        ):
            assert get_room_id("failed", 1) == "room-id"
    finally:
        get_room_id.cache_clear()
    post.assert_called_once_with(url=options["room_search_url"], json={"query": "priority-room"}, headers={})
