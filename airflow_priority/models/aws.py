from ..constants import AWSDefaultMetric, AWSDefaultNamespace
from .base import BaseConfiguration

__all__ = ("AwsConfiguration",)


class AwsConfiguration(BaseConfiguration):
    region: str = "us-east-1"
    namespace: str = AWSDefaultNamespace
    metric: str = AWSDefaultMetric
