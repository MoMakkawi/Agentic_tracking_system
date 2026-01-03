"""
Filter models for group queries.

This module contains Pydantic models for validating and structuring
filter parameters used in group queries.
"""

from typing import Optional, List
from pydantic import BaseModel, Field
from utils import GroupItemDTO


class GroupFilters(BaseModel):
    """
    Model for group filter parameters.
    
    This model encapsulates all possible filter criteria for student group queries.
    """
    
    group_name: Optional[str] = Field(None, description="Filter by group name (partial match)")
    member_uid: Optional[str] = Field(None, description="Filter by member UID present in group")
    min_members: Optional[int] = Field(None, ge=0, description="Minimum number of members in group")
    max_members: Optional[int] = Field(None, ge=0, description="Maximum number of members in group")
    
    def has_filters(self) -> bool:
        """Check if any filters are set."""
        return any([
            self.group_name is not None,
            self.member_uid is not None,
            self.min_members is not None,
            self.max_members is not None,
        ])


class PaginatedGroupResponse(BaseModel):
    """Response model for paginated group data."""
    
    items: List[GroupItemDTO]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")
