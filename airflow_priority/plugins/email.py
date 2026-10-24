from airflow.utils.email import send_email

from ..common import BackendContext, DagStatus, format_message, get_config_option

__all__ = ("send_metric",)


def send_metric(dag_id: str, priority: int, tag: DagStatus, context: BackendContext) -> None:
    if tag != "failed" and get_config_option("email", f"send_{tag}", default="false").lower() != "true":
        return
    send_email(
        to=get_config_option("email", "to"),
        subject=f'[Airflow P{priority}] DAG "{dag_id}" {tag}',
        html_content=f"<p>{format_message(dag_id, priority, tag, context, html=True)}</p>",
    )
