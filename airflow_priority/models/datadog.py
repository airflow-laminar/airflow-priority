from typing import List

from pydantic import Field

from ..constants import DataDogDefaultMetric
from .base import BaseConfiguration

__all__ = ("DataDogConfiguration",)


class DataDogConfiguration(BaseConfiguration):
    host: str = "https://api.datadoghq.com"
    api_key: str
    metric: str = DataDogDefaultMetric
    tags: List[str] = Field(default_factory=list)
