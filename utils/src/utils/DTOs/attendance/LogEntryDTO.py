from pydantic import BaseModel, Field

class LogEntryDTO(BaseModel):
    """DTO for a single attendance log entry."""
    ts: str = Field(..., description="Timestamp of the log entry")
    uid: str = Field(..., description="User ID (UID) recorded")
