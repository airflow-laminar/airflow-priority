from typing import Optional

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
    update_message: Optional[bool] = False
    send_running: Optional[bool] = False
    send_success: Optional[bool] = False
    failed_color: Optional[str] = None
    running_color: Optional[str] = None
    success_color: Optional[str] = None
    room_name_P1: Optional[str] = None
    room_name_P2: Optional[str] = None
    room_name_P3: Optional[str] = None
    room_name_P4: Optional[str] = None
    room_name_P5: Optional[str] = None
    room_name_failed: Optional[str] = None
    room_name_success: Optional[str] = None
    room_name_running: Optional[str] = None
    room_name_failed_P1: Optional[str] = None
    room_name_failed_P2: Optional[str] = None
    room_name_failed_P3: Optional[str] = None
    room_name_failed_P4: Optional[str] = None
    room_name_failed_P5: Optional[str] = None
    room_name_success_P1: Optional[str] = None
    room_name_success_P2: Optional[str] = None
    room_name_success_P3: Optional[str] = None
    room_name_success_P4: Optional[str] = None
    room_name_success_P5: Optional[str] = None
    room_name_running_P1: Optional[str] = None
    room_name_running_P2: Optional[str] = None
    room_name_running_P3: Optional[str] = None
    room_name_running_P4: Optional[str] = None
    room_name_running_P5: Optional[str] = None
