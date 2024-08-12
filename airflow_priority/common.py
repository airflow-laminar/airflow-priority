import os
from pathlib import Path
from types import MappingProxyType
from typing import Literal, Optional, Tuple

from airflow.models.dagrun import DagRun

__all__ = (
    "has_priority_tag",
    "get_config_option",
    "DagStatus",
    "PriorityTags",
    "AirflowPriorityConfigurationOptionNotFound",
)


DagStatus = Literal["running", "success", "failed"]

PriorityTags = MappingProxyType(
    {
        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4,
        "P5": 5,
    }
)


class AirflowPriorityConfigurationOptionNotFound(RuntimeError): ...


def get_config_option(section, key, required=True, default=None):
    try:
        from airflow_config import ConfigNotFoundError, Configuration

        try:
            config = Configuration.load("config", "config", basepath=str(Path(os.environ.get("AIRFLOW_HOME", "")) / "dags"), _offset=4)
            ret = getattr(getattr(config.extensions.get("priority", None), section, None), key, None)
            if ret is not None:
                return ret
        except ConfigNotFoundError:
            # SKIP
            pass
    except ImportError:
        # SKIP
        pass

    try:
        import airflow.configuration

        config_option = airflow.configuration.conf.get(f"priority.{section}", key, default)
        if not config_option and required:
            raise AirflowPriorityConfigurationOptionNotFound(f"{section}.{key}")
        return config_option
    except Exception:
        raise AirflowPriorityConfigurationOptionNotFound(f"{section}.{key}")


def has_priority_tag(dag_run: DagRun) -> Optional[Tuple[str, int]]:
    dag = dag_run.dag
    dag_id = dag_run.dag_id
    tags = dag.tags
    if tags:
        for tag in tags:
            priority = PriorityTags.get(tag.upper())
            if priority:
                return dag_id, priority
    return dag_id, None
