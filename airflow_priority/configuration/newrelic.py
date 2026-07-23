from pydantic import Field

from ..constants import NewRelicDefaultMetric
from .base import BaseConfiguration

__all__ = ("NewRelicConfiguration",)


class NewRelicConfiguration(BaseConfiguration):
    api_key: str
    metric: str = NewRelicDefaultMetric
    tags: dict[str, str] = Field(default_factory=dict)
