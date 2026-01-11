from pydantic import BaseModel, Field
from typing import List

class DeviceAlertDTO(BaseModel):
    """DTO for device validation alerts."""
    id: int = Field(..., description="Unique alert identifier")
    session_id: int = Field(..., description="ID of the session where alert triggered")
    device_id: str = Field(..., description="Device ID associated with the alert")
    reasons: List[str] = Field(..., description="List of reasons for the alert")
