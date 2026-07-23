from .base import BaseConfiguration

__all__ = ("SymphonyConfiguration",)


class SymphonyConfiguration(BaseConfiguration):
    message_create_url: str
    cert_file: str
    key_file: str
    session_auth: str
    key_auth: str
    room_search_url: str

    room_name: str
    update_message: bool | None = False
    send_running: bool | None = False
    send_success: bool | None = False
    failed_color: str | None = None
    running_color: str | None = None
    success_color: str | None = None
    room_name_P1: str | None = None
    room_name_P2: str | None = None
    room_name_P3: str | None = None
    room_name_P4: str | None = None
    room_name_P5: str | None = None
    room_name_failed: str | None = None
    room_name_success: str | None = None
    room_name_running: str | None = None
    room_name_failed_P1: str | None = None
    room_name_failed_P2: str | None = None
    room_name_failed_P3: str | None = None
    room_name_failed_P4: str | None = None
    room_name_failed_P5: str | None = None
    room_name_success_P1: str | None = None
    room_name_success_P2: str | None = None
    room_name_success_P3: str | None = None
    room_name_success_P4: str | None = None
    room_name_success_P5: str | None = None
    room_name_running_P1: str | None = None
    room_name_running_P2: str | None = None
    room_name_running_P3: str | None = None
    room_name_running_P4: str | None = None
    room_name_running_P5: str | None = None
