from pydantic import BaseModel, Field
from datetime import datetime
from typing import List

class TimestampAlertDTO(BaseModel):
    """DTO for timestamp validation alerts."""
    id: int = Field(..., description="Unique alert identifier")
    uid: str = Field(..., description="User ID (UID) involved")
    timestamp: datetime = Field(..., description="Timestamp of the alert")
    session_id: int = Field(..., description="Session ID associated with the alert")
    device_id: str = Field(..., description="Device ID")
    reasons: List[str] = Field(..., description="List of reasons for the alert")
