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
        tmpl = airflow_config_base_setup.get_template("airflow.cfg.alt").render()
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
        tmpl = airflow_config_base_setup.get_template("airflow.cfg").render()
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
