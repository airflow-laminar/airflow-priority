from .base import BaseConfiguration

__all__ = ("EmailConfiguration",)


class EmailConfiguration(BaseConfiguration):
    to: str | list[str]
    send_running: bool = False
    send_success: bool = False
