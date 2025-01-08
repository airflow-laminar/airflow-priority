from pathlib import Path

conf_text = """# @package _global_
_target_: airflow_config.Configuration
default_args:
  _target_: airflow_config.TaskArgs
  owner: test
extensions:
  priority:
    _target_: airflow_config.PriorityConfiguration
    slack:
      _target_: airflow_config.SlackConfiguration
      token: abc
      channel: def
"""


def test_config_loading_via_airflow_config(airflow_config, dag_run):
    dags_path = Path(airflow_config) / "dags"
    conf_path = dags_path / "config"
    conf_path.mkdir(parents=True, exist_ok=True)
    conf_file = conf_path / "config.yaml"
    conf_file.write_text(conf_text)

    from airflow_config import Configuration

    config = Configuration.load("config", "config", basepath=str(dags_path), _offset=4)
    ret = getattr(getattr(config.extensions.get("priority", None), "slack", None), "token", None)
    assert ret == "abc"


def test_call_plugin_via_airflow_config(airflow_config, dag_run):
    dags_path = Path(airflow_config) / "dags"
    conf_path = dags_path / "config"
    conf_path.mkdir(parents=True, exist_ok=True)
    conf_file = conf_path / "config.yaml"
    conf_file.write_text(conf_text)
    from airflow_priority.plugins.slack import get_client

    client = get_client()
    assert client is not None
    assert client.token == "abc"
