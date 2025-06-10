from typing import Optional

from .base import BaseConfiguration

__all__ = ("SlackConfiguration",)


class SlackConfiguration(BaseConfiguration):
    token: str
    channel: str
    update_message: Optional[bool] = False
    send_running: Optional[bool] = False
    send_success: Optional[bool] = False
    failed_color: Optional[str] = None
    running_color: Optional[str] = None
    success_color: Optional[str] = None
    channel_P1: Optional[str] = None
    channel_P2: Optional[str] = None
    channel_P3: Optional[str] = None
    channel_P4: Optional[str] = None
    channel_P5: Optional[str] = None
    channel_failed: Optional[str] = None
    channel_success: Optional[str] = None
    channel_running: Optional[str] = None
    channel_failed_P1: Optional[str] = None
    channel_failed_P2: Optional[str] = None
    channel_failed_P3: Optional[str] = None
    channel_failed_P4: Optional[str] = None
    channel_failed_P5: Optional[str] = None
    channel_success_P1: Optional[str] = None
    channel_success_P2: Optional[str] = None
    channel_success_P3: Optional[str] = None
    channel_success_P4: Optional[str] = None
    channel_success_P5: Optional[str] = None
    channel_running_P1: Optional[str] = None
    channel_running_P2: Optional[str] = None
    channel_running_P3: Optional[str] = None
    channel_running_P4: Optional[str] = None
    channel_running_P5: Optional[str] = None
