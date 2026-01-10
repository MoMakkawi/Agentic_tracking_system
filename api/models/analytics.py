from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AttendanceTrendItem(BaseModel):
    name: str = Field(..., description="Display label (mm/dd or mm/dd/yyyy)")
    fullDate: str = Field(..., description="YYYY-MM-DD")
    attendance: int
    unassigned: int
    recorded: int
    sessions: int

class GroupTrendItem(BaseModel):
    date: str
    presence: int

class EnrichedGroupItem(BaseModel):
    name: str
    members: List[str]
    member_count: int
    attendanceTrend: List[GroupTrendItem]
    avgAttendance: int

class MultiTrendDataPoint(BaseModel):
    date: str
    # We use a dict for dynamic group names as keys
    data: Dict[str, int] = Field(default_factory=dict)

    class Config:
        extra = "allow"

class GroupAnalyticsResponse(BaseModel):
    groups: List[EnrichedGroupItem]
    multiTrendData: List[Dict[str, Any]]
    groupColors: Dict[str, str]
