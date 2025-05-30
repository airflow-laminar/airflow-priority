import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from jinja2 import DictLoader, Environment


@pytest.fixture(autouse=True)
def airflow_config_base_setup():
    config_template = (Path(__file__).parent / "airflow.cfg.jinja").read_text()
    config_template_alt = (Path(__file__).parent / "airflow.cfg2.jinja").read_text()
    base_config_template = (Path(__file__).parent / "airflow.cfg.base.jinja").read_text()
    j2 = Environment(
        loader=DictLoader({"airflow.cfg": config_template, "airflow.cfg.alt": config_template_alt, "airflow.cfg.base": base_config_template}),
        trim_blocks=True,
    )
    yield j2


@pytest.fixture(scope="function")
def airflow_config_alt(airflow_config_base_setup):
    with TemporaryDirectory() as td:
        tmpl = airflow_config_base_setup.get_template("airflow.cfg.alt").render(
            DATADOG_HOST=os.environ.get("DATADOG_HOST", ""),
            DATADOG_API_KEY=os.environ.get("DATADOG_API_KEY", ""),
            DISCORD_TOKEN=os.environ.get("DISCORD_TOKEN", ""),
            DISCORD_CHANNEL=os.environ.get("DISCORD_CHANNEL", ""),
            NEWRELIC_API_KEY=os.environ.get("NEWRELIC_API_KEY", ""),
            OPSGENIE_API_KEY=os.environ.get("OPSGENIE_API_KEY", ""),
            SLACK_TOKEN=os.environ.get("SLACK_TOKEN", ""),
            SLACK_CHANNEL=os.environ.get("SLACK_CHANNEL", ""),
            SYMPHONY_ROOM_NAME=os.environ.get("SYMPHONY_ROOM_NAME", ""),
            SYMPHONY_MESSAGE_CREATE_URL=os.environ.get("SYMPHONY_MESSAGE_CREATE_URL", ""),
            SYMPHONY_CERT_FILE=os.environ.get("SYMPHONY_CERT_FILE", ""),
            SYMPHONY_KEY_FILE=os.environ.get("SYMPHONY_KEY_FILE", ""),
            SYMPHONY_SESSION_AUTH=os.environ.get("SYMPHONY_SESSION_AUTH", ""),
            SYMPHONY_KEY_AUTH=os.environ.get("SYMPHONY_KEY_AUTH", ""),
            SYMPHONY_ROOM_SEARCH_URL=os.environ.get("SYMPHONY_ROOM_SEARCH_URL", ""),
        )
        (Path(td) / "airflow.cfg").write_text(tmpl)
        os.environ["AIRFLOW_HOME"] = str(Path(td))
        os.environ["AIRFLOW_CONFIG"] = str((Path(td) / "airflow.cfg"))
        import airflow.configuration

        airflow.configuration.AIRFLOW_HOME = os.environ["AIRFLOW_HOME"]
        airflow.configuration.AIRFLOW_CONFIG = os.environ["AIRFLOW_CONFIG"]
        airflow_config_parser = airflow.configuration.AirflowConfigParser()
        airflow.configuration.load_standard_airflow_configuration(airflow_config_parser)
        airflow_config_parser.validate()
        airflow.configuration.conf = airflow_config_parser
        yield str(Path(td))


@pytest.fixture(scope="function")
def airflow_config(airflow_config_base_setup):
    with TemporaryDirectory() as td:
        tmpl = airflow_config_base_setup.get_template("airflow.cfg").render(
            DATADOG_HOST=os.environ.get("DATADOG_HOST", ""),
            DATADOG_API_KEY=os.environ.get("DATADOG_API_KEY", ""),
            DISCORD_TOKEN=os.environ.get("DISCORD_TOKEN", ""),
            DISCORD_CHANNEL=os.environ.get("DISCORD_CHANNEL", ""),
            NEWRELIC_API_KEY=os.environ.get("NEWRELIC_API_KEY", ""),
            OPSGENIE_API_KEY=os.environ.get("OPSGENIE_API_KEY", ""),
            SLACK_TOKEN=os.environ.get("SLACK_TOKEN", ""),
            SLACK_CHANNEL=os.environ.get("SLACK_CHANNEL", ""),
            SYMPHONY_ROOM_NAME=os.environ.get("SYMPHONY_ROOM_NAME", ""),
            SYMPHONY_MESSAGE_CREATE_URL=os.environ.get("SYMPHONY_MESSAGE_CREATE_URL", ""),
            SYMPHONY_CERT_FILE=os.environ.get("SYMPHONY_CERT_FILE", ""),
            SYMPHONY_KEY_FILE=os.environ.get("SYMPHONY_KEY_FILE", ""),
            SYMPHONY_SESSION_AUTH=os.environ.get("SYMPHONY_SESSION_AUTH", ""),
            SYMPHONY_KEY_AUTH=os.environ.get("SYMPHONY_KEY_AUTH", ""),
            SYMPHONY_ROOM_SEARCH_URL=os.environ.get("SYMPHONY_ROOM_SEARCH_URL", ""),
        )
        (Path(td) / "airflow.cfg").write_text(tmpl)
        os.environ["AIRFLOW_HOME"] = str(Path(td))
        os.environ["AIRFLOW_CONFIG"] = str((Path(td) / "airflow.cfg"))
        import airflow.configuration

        airflow.configuration.AIRFLOW_HOME = os.environ["AIRFLOW_HOME"]
        airflow.configuration.AIRFLOW_CONFIG = os.environ["AIRFLOW_CONFIG"]
        airflow_config_parser = airflow.configuration.AirflowConfigParser()
        airflow.configuration.load_standard_airflow_configuration(airflow_config_parser)
        airflow_config_parser.validate()
        airflow.configuration.conf = airflow_config_parser
        yield str(Path(td))


@pytest.fixture(scope="function", autouse=True)
def dag_run():
    from unittest.mock import MagicMock

    from airflow.models.dagrun import DagRun

    dag_run = DagRun("UNIT TEST")
    dag_run.dag = MagicMock()
    dag_run.dag.tags = ["P1"]
    return dag_run


@pytest.fixture(scope="function", autouse=True)
def dag_run_p3():
    from unittest.mock import MagicMock

    from airflow.models.dagrun import DagRun

    dag_run = DagRun("UNIT TEST")
    dag_run.dag = MagicMock()
    dag_run.dag.tags = ["P3"]
    return dag_run


@pytest.fixture(scope="function", autouse=True)
def new_tracker():
    from airflow_priority.tracker import Tracker

    yield Tracker()
