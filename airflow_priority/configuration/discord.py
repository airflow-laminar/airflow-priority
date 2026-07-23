from .base import BaseConfiguration

__all__ = ("DiscordConfiguration",)


class DiscordConfiguration(BaseConfiguration):
    token: str
    channel: str
    update_message: bool | None = False
    send_running: bool | None = False
    send_success: bool | None = False
    failed_color: str | None = None
    running_color: str | None = None
    success_color: str | None = None
    channel_P1: str | None = None
    channel_P2: str | None = None
    channel_P3: str | None = None
    channel_P4: str | None = None
    channel_P5: str | None = None
    channel_failed: str | None = None
    channel_success: str | None = None
    channel_running: str | None = None
    channel_failed_P1: str | None = None
    channel_failed_P2: str | None = None
    channel_failed_P3: str | None = None
    channel_failed_P4: str | None = None
    channel_failed_P5: str | None = None
    channel_success_P1: str | None = None
    channel_success_P2: str | None = None
    channel_success_P3: str | None = None
    channel_success_P4: str | None = None
    channel_success_P5: str | None = None
    channel_running_P1: str | None = None
    channel_running_P2: str | None = None
    channel_running_P3: str | None = None
    channel_running_P4: str | None = None
    channel_running_P5: str | None = None
