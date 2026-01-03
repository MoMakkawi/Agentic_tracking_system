from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
from .MatchedSessionDTO import MatchedSessionDTO
from .LogEntryDTO import LogEntryDTO

@dataclass
class SessionDTO:
    session_id: int
    device_id: str
    session_context: str
    matched_sessions: List[MatchedSessionDTO]
    received_at: datetime
    logs_date: str
    recorded_count: int
    unique_count: int
    redundant_uids: Dict[str, Any]
    logs: List[LogEntryDTO]
