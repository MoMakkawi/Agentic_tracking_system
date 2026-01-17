# SPDX-FileCopyrightText: 2025-present MoMakkawi <MoMakkawi@hotmail.com>
#
# SPDX-License-Identifier: MIT

# src/utils/__init__.py
from .src.utils.Secrets import Secrets
from .src.utils.config import load_config, get_config
from .src.utils.logger import logger
from .src.utils.helpers.time import TimestampHelper
from .src.utils.models.gemini import GeminiModel
from .src.utils.models.ragarenn import RagarennModel
from .src.utils.storage.factory import RepositoryFactory
from .src.utils.storage.base import FileRepository
from .src.utils.storage.json_repo import JsonRepository
from .src.utils.storage.jsonl_repo import JsonlRepository
from .src.utils.storage.csv_repo import CsvRepository
from .src.utils.storage.ics_repo import IcsRepository
from .src.utils.DTOs.attendance.SessionDTO import SessionDTO
from .src.utils.DTOs.attendance.MatchedSessionDTO import MatchedSessionDTO
from .src.utils.DTOs.attendance.LogEntryDTO import LogEntryDTO
from .src.utils.DTOs.groups.GroupsDTO import GroupsDTO
from .src.utils.DTOs.groups.GroupItemDTO import GroupItemDTO
from .src.utils.DTOs.alerts.DeviceAlertDTO import DeviceAlertDTO
from .src.utils.DTOs.alerts.IdentityAlertDTO import IdentityAlertDTO
from .src.utils.DTOs.alerts.TimestampAlertDTO import TimestampAlertDTO
from .src.utils.mappers.session_mappers import (
    map_to_session_dto,
    map_to_session_dtos,
    map_to_matched_session_dto,
    map_to_log_entry_dto,
    parse_datetime
)
from .src.utils.mappers.alert_mappers import (
    map_to_device_alert_dto,
    map_to_identity_alert_dto,
    map_to_timestamp_alert_dto,
    split_semicolon_list
)
from .src.utils.mappers.group_mappers import map_to_group_item_dto

__all__ = [
    "logger",
    "Secrets",

    #Config
    "load_config",
    "get_config",

    #Helpers
    "TimestampHelper",

    #LLM models
    "GeminiModel",
    "RagarennModel",

    #Storage
    "FileRepository",
    "RepositoryFactory",
    "JsonRepository",
    "JsonlRepository",
    "CsvRepository",
    "IcsRepository",

    #DTOs
    "SessionDTO",
    "MatchedSessionDTO",
    "LogEntryDTO",
    "GroupsDTO",
    "GroupItemDTO",
    "DeviceAlertDTO",
    "IdentityAlertDTO",
    "TimestampAlertDTO",
]