from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from airflow_priority.tracker import Tracker


@pytest.mark.parametrize("event", ["running", "success", "failed"])
def test_backend_threshold_does_not_skip_later_backends(event):
    tracker = Tracker()
    filtered = Mock()
    eligible = Mock()
    tracker.backends = {"filtered": filtered, "eligible": eligible}
    tracker.thresholds = {"filtered": 2, "eligible": 5}
    run = SimpleNamespace(id=42, dag_id="priority-routing", dag=SimpleNamespace(tags=["P3"]))

    getattr(tracker, event)(run)

    filtered.assert_not_called()
    eligible.assert_called_once_with(run.dag_id, 3, event, tracker.dagruns[("eligible", run.id)])


@pytest.mark.parametrize("event", ["running", "success", "failed"])
def test_backend_error_does_not_skip_later_backends(event, caplog):
    tracker = Tracker()
    broken = Mock(side_effect=RuntimeError("Backend unavailable"))
    eligible = Mock()
    tracker.backends = {"broken": broken, "eligible": eligible}
    run = SimpleNamespace(id=42, dag_id="priority-routing", dag=SimpleNamespace(tags=["P3"]))

    getattr(tracker, event)(run)

    assert "Backend unavailable" in caplog.text
    eligible.assert_called_once()
