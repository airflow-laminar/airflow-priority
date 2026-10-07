from unittest.mock import Mock

import pytest


@pytest.mark.parametrize("state,event", [("running", "running"), ("success", "success"), ("failed", "failed")])
def test_listener_dispatches_dag_run_events(state, event, dag_run, monkeypatch):
    from airflow.listeners.listener import ListenerManager

    from airflow_priority import plugin

    tracker = Mock()
    monkeypatch.setattr(plugin, "tracker_inst", tracker)
    manager = ListenerManager()
    manager.add_listener(plugin)
    getattr(manager.hook, f"on_dag_run_{state}")(dag_run=dag_run, msg="Test DAG state change")
    getattr(tracker, event).assert_called_once_with(dag_run)


def test_plugin():
    try:
        from airflow import DAG  # noqa: F401
    except ImportError:
        return pytest.skip("Airflow not available in this environment")

    import airflow_priority.plugin  # noqa: F401
