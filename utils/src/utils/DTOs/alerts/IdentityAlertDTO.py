from pydantic import BaseModel, Field
from typing import List

class IdentityAlertDTO(BaseModel):
    """DTO for identity validation alerts."""
    id: int = Field(..., description="Unique alert identifier")
    uid: str = Field(..., description="User ID (UID) involved in the alert")
    device_id: str = Field(..., description="Device ID where the alert occurred")
    normal_sessions_count: int = Field(..., description="Count of normal sessions for this user")
    repeated_anomaly_count: int = Field(..., description="Count of repeated anomalies")
    anomaly_sessions: List[int] = Field(..., description="List of session IDs flagged as anomalies")
    reasons: List[str] = Field(..., description="List of reasons for the alert")
