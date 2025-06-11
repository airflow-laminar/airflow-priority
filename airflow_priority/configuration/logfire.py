from ..constants import LogfireDefaultMetric
from .base import BaseConfiguration

__all__ = ("LogfireConfiguration",)


class LogfireConfiguration(BaseConfiguration):
    token: str
    metric: str = LogfireDefaultMetric
