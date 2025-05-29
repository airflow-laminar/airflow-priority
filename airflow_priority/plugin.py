import sys

from airflow.listeners import hookimpl
from airflow.models.dagrun import DagRun
from airflow.plugins_manager import AirflowPlugin

from .tracker import tracker_inst


@hookimpl
def on_dag_run_running(dag_run: DagRun, msg: str):
    tracker_inst.running(dag_run)


@hookimpl
def on_dag_run_success(dag_run: DagRun, msg: str):
    tracker_inst.success(dag_run)


@hookimpl
def on_dag_run_failed(dag_run: DagRun, msg: str):
    tracker_inst.failed(dag_run)


class AirflowPriorityPlugin(AirflowPlugin):
    name = "AirflowPriorityPlugin"
    listeners = [sys.modules[__name__]]
