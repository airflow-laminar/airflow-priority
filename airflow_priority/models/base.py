from ccflow import BaseModel

__all__ = ("BaseConfiguration",)


class BaseConfiguration(BaseModel):
    threshold: int = 6
