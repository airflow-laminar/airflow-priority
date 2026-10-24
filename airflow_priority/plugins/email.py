from html import escape
from typing import Any

from airflow.utils.email import send_email

from ..common import DagStatus, get_config_option

__all__ = ("send_metric",)


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: dict[DagStatus, Any]) -> None:
    if tag != "failed" and get_config_option("email", f"send_{tag}", default="false").lower() != "true":
        return
    send_email(
        to=get_config_option("email", "to"),
        subject=f'[Airflow P{priority}] DAG "{dag_id}" {tag}',
        html_content=f"<p>A P{priority} DAG &quot;{escape(dag_id)}&quot; has been marked &quot;{tag}&quot;.</p>",
    )
