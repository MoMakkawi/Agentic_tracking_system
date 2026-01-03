"""
Data mappers for converting raw data to DTOs.

This module contains functions for mapping raw dictionary data
to Data Transfer Objects (DTOs) used throughout the API.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime

from utils import SessionDTO, MatchedSessionDTO, LogEntryDTO
from utils import logger


def parse_datetime(value: Any) -> Optional[datetime]:
    """
    Parse a datetime value from various formats.
    
    Args:
        value: The value to parse (can be string, datetime, or None)
        
    Returns:
        Parsed datetime object or None if parsing fails
    """
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return value
    
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to parse datetime value '{value}': {e}")
            return None
    
    return None


def map_to_matched_session_dto(data: Dict[str, Any]) -> MatchedSessionDTO:
    """
    Map raw dictionary data to MatchedSessionDTO.
    
    Args:
        data: Raw dictionary containing matched session data
        
    Returns:
        MatchedSessionDTO instance
    """
    return MatchedSessionDTO(
        id=data.get("id"),
        summary=data.get("summary"),
        start=data.get("start"),
        end=data.get("end")
    )


def map_to_log_entry_dto(data: Dict[str, Any]) -> LogEntryDTO:
    """
    Map raw dictionary data to LogEntryDTO.
    
    Args:
        data: Raw dictionary containing log entry data
        
    Returns:
        LogEntryDTO instance
    """
    return LogEntryDTO(
        uid=data.get("uid"),
        ts=data.get("ts")
    )


def map_to_session_dto(data: Dict[str, Any]) -> SessionDTO:
    """
    Map raw dictionary data to SessionDTO.
    
    This function handles the complete mapping of a session record,
    including nested matched sessions and log entries.
    
    Args:
        data: Raw dictionary containing session data
        
    Returns:
        SessionDTO instance
    """
    # Map matched sessions
    matched_raw = data.get("matched_sessions", [])
    matched_dtos = [map_to_matched_session_dto(m) for m in matched_raw]
    
    # Map logs
    logs_raw = data.get("logs", [])
    logs_dtos = [map_to_log_entry_dto(log) for log in logs_raw]
    
    # Parse received_at datetime
    received_at = parse_datetime(data.get("received_at"))
    
    # Create and return DTO
    return SessionDTO(
        session_id=data.get("session_id"),
        device_id=data.get("device_id"),
        session_context=data.get("session_context"),
        matched_sessions=matched_dtos,
        received_at=received_at,
        logs_date=data.get("logs_date"),
        recorded_count=data.get("recorded_count"),
        unique_count=data.get("unique_count"),
        redundant_uids=data.get("redundant_uids", {}),
        logs=logs_dtos
    )


def map_to_session_dtos(data_list: List[Dict[str, Any]]) -> List[SessionDTO]:
    """
    Map a list of raw dictionaries to SessionDTO instances.
    
    Args:
        data_list: List of raw dictionaries containing session data
        
    Returns:
        List of SessionDTO instances
    """
    return [map_to_session_dto(item) for item in data_list]
