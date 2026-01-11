from pydantic import BaseModel, Field
from datetime import datetime

class MatchedSessionDTO(BaseModel):
    """DTO for a session matched across different criteria."""
    id: str = Field(..., description="Unique identifier for the matched session")
    summary: str = Field(..., description="Summary of the match")
    start: datetime = Field(..., description="Start time of the matched session")
    end: datetime = Field(..., description="End time of the matched session")
