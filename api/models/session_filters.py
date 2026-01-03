"""
Filter models for session queries.

This module contains Pydantic models for validating and structuring
filter parameters used in session queries.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator

from api.exceptions import InvalidDateFormatError


class SessionFilters(BaseModel):
    """
    Model for session filter parameters.
    
    This model encapsulates all possible filter criteria for session queries,
    providing type safety and validation.
    """
    
    # Exact match filters
    session_id: Optional[int] = Field(None, description="Filter by exact session ID")
    device_id: Optional[str] = Field(None, description="Filter by exact device ID")
    logs_date: Optional[str] = Field(None, description="Filter by exact logs date (YYYY-MM-DD)")
    
    # Range filters for dates
    received_at_from: Optional[datetime] = Field(None, description="Filter sessions received from this date")
    received_at_to: Optional[datetime] = Field(None, description="Filter sessions received until this date")
    
    # Range filters for counts
    recorded_count_min: Optional[int] = Field(None, ge=0, description="Minimum recorded count")
    recorded_count_max: Optional[int] = Field(None, ge=0, description="Maximum recorded count")
    unique_count_min: Optional[int] = Field(None, ge=0, description="Minimum unique count")
    unique_count_max: Optional[int] = Field(None, ge=0, description="Maximum unique count")
    
    # Text search
    session_context_contains: Optional[str] = Field(None, description="Filter by session context containing this text")
    
    def has_filters(self) -> bool:
        """
        Check if any filters are set.
        
        Returns:
            True if at least one filter is set, False otherwise
        """
        return any([
            self.session_id is not None,
            self.device_id is not None,
            self.logs_date is not None,
            self.received_at_from is not None,
            self.received_at_to is not None,
            self.recorded_count_min is not None,
            self.recorded_count_max is not None,
            self.unique_count_min is not None,
            self.unique_count_max is not None,
            self.session_context_contains is not None,
        ])


class PaginationParams(BaseModel):
    """
    Model for pagination parameters.
    
    This model encapsulates pagination settings with validation.
    """
    
    page: int = Field(1, ge=1, description="Page number (starts from 1)")
    page_size: int = Field(10, ge=1, le=100, description="Number of items per page")
    
    def get_slice_indices(self) -> tuple[int, int]:
        """
        Calculate start and end indices for slicing.
        
        Returns:
            Tuple of (start_index, end_index)
        """
        start_idx = (self.page - 1) * self.page_size
        end_idx = start_idx + self.page_size
        return start_idx, end_idx


class SortParams(BaseModel):
    """
    Model for sorting parameters.
    
    This model encapsulates sorting settings with validation.
    """
    
    order_by: Optional[str] = Field(None, description="Field to order by")
    order_direction: str = Field("asc", pattern="^(asc|desc)$", description="Order direction: asc or desc")
    
    def is_descending(self) -> bool:
        """
        Check if sort direction is descending.
        
        Returns:
            True if descending, False if ascending
        """
        return self.order_direction == "desc"
