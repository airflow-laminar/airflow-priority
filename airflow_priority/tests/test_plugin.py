import pytest


def test_plugin():
    try:
        from airflow import DAG  # noqa: F401
    except ImportError:
        return pytest.skip("Airflow not available in this environment")

    import airflow_priority.plugin  # noqa: F401
