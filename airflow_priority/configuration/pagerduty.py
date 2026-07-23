from ..constants import PagerDutyDefaultSource
from .base import BaseConfiguration

__all__ = ("PagerDutyConfiguration",)


class PagerDutyConfiguration(BaseConfiguration):
    routing_key: str
    source: str = PagerDutyDefaultSource
    update: bool | None = True
