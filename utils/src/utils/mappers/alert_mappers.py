"""
Data mappers for alert-related DTOs.

This module contains functions for mapping raw dictionary data
to alert Data Transfer Objects (DTOs).
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from utils import DeviceAlertDTO, IdentityAlertDTO, TimestampAlertDTO
from .session_mappers import parse_datetime


def split_semicolon_list(value: Any, separator: str = ";") -> List[str]:
    """
    Split a semicolon-separated string into a list of strings.
    
    Args:
        value: The value to split
        separator: The separator to use (default: ";")
        
    Returns:
        List of strings
    """
    if not value or not isinstance(value, str):
        return [str(value)] if value is not None else []
    
    return [s.strip() for s in value.split(separator.strip()) if s.strip()]


def map_to_device_alert_dto(data: Dict[str, Any]) -> DeviceAlertDTO:
    """
    Map raw dictionary data to DeviceAlertDTO.
    
    Args:
        data: Raw dictionary containing device alert data
        
    Returns:
        DeviceAlertDTO instance
    """
    reasons = data.get("reasons")
    if isinstance(reasons, str):
        reasons = split_semicolon_list(reasons)
    elif not isinstance(reasons, list):
        reasons = [str(reasons)] if reasons is not None else []
        
    return DeviceAlertDTO(
        id=int(data.get("id", 0)),
        session_id=int(data.get("session_id", 0)),
        device_id=data.get("device_id", ""),
        reasons=reasons
    )


def map_to_identity_alert_dto(data: Dict[str, Any]) -> IdentityAlertDTO:
    """
    Map raw dictionary data to IdentityAlertDTO.
    
    Args:
        data: Raw dictionary containing identity alert data
        
    Returns:
        IdentityAlertDTO instance
    """
    reasons = data.get("reasons")
    if isinstance(reasons, str):
        reasons = split_semicolon_list(reasons)
    elif not isinstance(reasons, list):
        reasons = [str(reasons)] if reasons is not None else []
        
    anomaly_sessions_raw = data.get("anomaly_sessions")
    anomaly_sessions = []
    if isinstance(anomaly_sessions_raw, str):
        sessions_list = split_semicolon_list(anomaly_sessions_raw, separator=";")
        anomaly_sessions = [int(s) for s in sessions_list if s.isdigit()]
    elif isinstance(anomaly_sessions_raw, list):
        anomaly_sessions = [int(s) for s in anomaly_sessions_raw if str(s).isdigit()]
        
    return IdentityAlertDTO(
        id=int(data.get("id", 0)),
        uid=data.get("uid", ""),
        device_id=data.get("device_id", ""),
        normal_sessions_count=int(data.get("normal_sessions_count", 0)),
        repeated_anomaly_count=int(data.get("repeated_anomaly_count", 0)),
        anomaly_sessions=anomaly_sessions,
        reasons=reasons
    )


def map_to_timestamp_alert_dto(data: Dict[str, Any]) -> TimestampAlertDTO:
    """
    Map raw dictionary data to TimestampAlertDTO.
    
    Args:
        data: Raw dictionary containing timestamp alert data
        
    Returns:
        TimestampAlertDTO instance
    """
    reasons = data.get("reasons")
    if isinstance(reasons, str):
        reasons = split_semicolon_list(reasons)
    elif not isinstance(reasons, list):
        reasons = [str(reasons)] if reasons is not None else []
        
    timestamp = parse_datetime(data.get("timestamp"))
    
    return TimestampAlertDTO(
        id=int(data.get("id", 0)),
        uid=data.get("uid", ""),
        timestamp=timestamp,
        session_id=int(data.get("session_id", 0)),
        device_id=data.get("device_id", ""),
        reasons=reasons
    )
