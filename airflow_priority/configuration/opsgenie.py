from ..constants import OpsGenieDefaultEntity
from .base import BaseConfiguration

__all__ = ("OpsGenieConfiguration",)


class OpsGenieConfiguration(BaseConfiguration):
    api_key: str
    entity: str = OpsGenieDefaultEntity
    update: bool | None = True
