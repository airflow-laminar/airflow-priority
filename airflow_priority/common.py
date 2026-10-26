import os
from collections.abc import Callable
from datetime import datetime
from functools import lru_cache
from html import escape
from pathlib import Path
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Literal, cast
from urllib.parse import quote

if TYPE_CHECKING:
    from airflow.models.dagrun import DagRun

__all__ = (
    "AirflowPriorityConfigurationOptionNotFound",
    "BackendContext",
    "BackendSpecificDagContext",
    "DagContextIdentifier",
    "DagStatus",
    "PriorityTags",
    "SendMetricFunction",
    "format_message",
    "get_config_option",
    "get_run_details",
    "has_priority_tag",
)


DagStatus = Literal["running", "success", "failed"]
BackendSpecificDagContext = Any
DagContextIdentifier = tuple[str, int]  # (backend, dag_instance_id)
BackendContext = dict[str, Any]
SendMetricFunction = Callable[[str, int, DagStatus, BackendContext], None]

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


def get_run_details(dag_run: "DagRun") -> dict[str, str]:
    """Return run identifiers, logical date, and the Airflow 2/3 UI URL."""
    dag_id = cast(str, dag_run.dag_id)
    details = {"dag_id": dag_id}
    logical_date = getattr(dag_run, "logical_date", None)
    if isinstance(logical_date, datetime):
        details["logical_date"] = logical_date.isoformat()
    run_id = getattr(dag_run, "run_id", None)
    if not isinstance(run_id, str) or not run_id:
        return details
    details["run_id"] = run_id
    try:
        from airflow import __version__
        from airflow.configuration import conf
    except ImportError:
        return details
    airflow3 = int(__version__.split(".")[0]) >= 3
    base_url = conf.get("api" if airflow3 else "webserver", "base_url", fallback=None)
    if base_url:
        dag_id = quote(dag_id, safe="")
        run_id = quote(run_id, safe="")
        suffix = f"/runs/{run_id}" if airflow3 else f"/grid?dag_run_id={run_id}"
        details["url"] = f"{base_url.rstrip('/')}/dags/{dag_id}{suffix}"
    return details


def format_message(dag_id: str, priority: int, tag: DagStatus, context: BackendContext, *, html: bool = False) -> str:
    """Format a notification with available run metadata."""
    parts = [f'A P{priority} DAG "{dag_id}" has been marked "{tag}"']
    run = context.get("run", {})
    for label, key in (("Run", "run_id"), ("Logical date", "logical_date")):
        if run.get(key):
            parts.append(f"{label}: {run[key]}")
    if html:
        parts = [escape(part) for part in parts]
        if run.get("url"):
            parts.append(f'<a href="{escape(run["url"], quote=True)}">Open DAG run</a>')
        return "<br/>".join(parts)
    if run.get("url"):
        parts.append(f"Run URL: {run['url']}")
    return "\n".join(parts)


@lru_cache
def get_config_option(section, key="", required=True, default=None):
    try:
        from airflow_config import ConfigNotFoundError, Configuration

        try:
            # TODO rework
            config = Configuration.load("config", "config", basepath=str(Path(os.environ.get("AIRFLOW_HOME", "")) / "dags"), _offset=4)
            ret = getattr(getattr((config.extensions or {}).get("priority", None), section, None), key, None)
            if ret is not None:
                return str(ret).lower() if isinstance(ret, bool) else ret
        except ConfigNotFoundError:
            # SKIP
            pass
    except ImportError:
        # SKIP
        pass

    config_option = default

    try:
        import airflow.configuration
        import airflow.exceptions

        if key:
            try:
                config_option = airflow.configuration.conf.get(f"priority.{section}", key, fallback=None)
            except airflow.exceptions.AirflowConfigException:
                config_option = None
            if not config_option:
                try:
                    # Try nested variant
                    config_option = airflow.configuration.conf.get("priority", f"{section}_{key}", fallback=default)
                except airflow.exceptions.AirflowConfigException:
                    pass
        else:
            try:
                config_option = airflow.configuration.conf.get("priority", section, fallback=default)
            except airflow.exceptions.AirflowConfigException:
                pass
        if not config_option:
            # restore default/None
            config_option = default
    except ImportError:
        pass
    if not config_option and required:
        raise AirflowPriorityConfigurationOptionNotFound(f"{section}.{key}")
    return config_option


def has_priority_tag(dag_run: "DagRun") -> tuple[str, int | None]:
    dag = dag_run.dag
    dag_id = cast(str, dag_run.dag_id)
    tags = dag.tags if dag is not None else []
    if tags:
        for tag in tags:
            priority = PriorityTags.get(tag.upper())
            if priority:
                return dag_id, priority
    return dag_id, None
