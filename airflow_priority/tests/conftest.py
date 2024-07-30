import os
from pathlib import Path
from tempfile import TemporaryDirectory

import pytest
from jinja2 import DictLoader, Environment


@pytest.fixture(autouse=True)
def airflow_config():
    config_template = (Path(__file__).parent / "airflow.cfg.jinja").read_text()
    j2 = Environment(loader=DictLoader({"airflow.cfg": config_template}), trim_blocks=True)
    with TemporaryDirectory() as td:
        tmpl = j2.get_template("airflow.cfg").render(
            SLACK_TOKEN=os.environ.get("SLACK_TOKEN", ""),
            SLACK_CHANNEL=os.environ.get("SLACK_CHANNEL", ""),
            DATADOG_HOST=os.environ.get("DATADOG_HOST", ""),
            DATADOG_API_KEY=os.environ.get("DATADOG_API_KEY", ""),
            NEWRELIC_API_KEY=os.environ.get("NEWRELIC_API_KEY", ""),
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
        yield


@pytest.fixture(scope="function", autouse=True)
def dag_run():
    from unittest.mock import MagicMock

    from airflow.models.dagrun import DagRun

    dag_run = DagRun("UNIT TEST")
    dag_run.dag = MagicMock()
    dag_run.dag.tags = ["P1"]
    return dag_run
