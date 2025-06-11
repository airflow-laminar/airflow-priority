from typing import Dict

from pydantic import Field

from ..constants import NewRelicDefaultMetric
from .base import BaseConfiguration

__all__ = ("NewRelicConfiguration",)


class NewRelicConfiguration(BaseConfiguration):
    api_key: str
    metric: str = NewRelicDefaultMetric
    tags: Dict[str, str] = Field(default_factory=dict)
