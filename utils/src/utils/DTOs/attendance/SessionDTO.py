from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from .MatchedSessionDTO import MatchedSessionDTO
from .LogEntryDTO import LogEntryDTO

class SessionDTO(BaseModel):
    """DTO for an attendance session."""
    session_id: int = Field(..., description="Unique session identifier")
    device_id: str = Field(..., description="Device ID where session was recorded")
    session_context: str = Field(..., description="Context string of the session")
    matched_sessions: List[MatchedSessionDTO] = Field(..., description="List of matched sessions")
    received_at: datetime = Field(..., description="Timestamp when the session was received")
    logs_date: str = Field(..., description="Date of the logs (YYYY-MM-DD)")
    recorded_count: int = Field(..., description="Total number of logs recorded")
    unique_count: int = Field(..., description="Count of unique UIDs")
    redundant_uids: Dict[str, Any] = Field(..., description="Dictionary of redundant UIDs")
    logs: List[LogEntryDTO] = Field(..., description="List of raw log entries")
    alert_count: int = Field(0, description="Number of alerts associated with this session")
    alerts: List[Dict[str, Any]] = Field(default_factory=list, description="List of detailed alerts")
