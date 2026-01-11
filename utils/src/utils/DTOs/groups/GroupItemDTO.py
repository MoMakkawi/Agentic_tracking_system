from pydantic import BaseModel, Field
from typing import List

class GroupItemDTO(BaseModel):
    """DTO for an individual group."""
    name: str = Field(..., description="Name of the group")
    members: List[str] = Field(..., description="List of member UIDs in the group")
    member_count: int = Field(..., description="Total count of members in the group")
