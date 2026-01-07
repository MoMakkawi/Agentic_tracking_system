"""
Filter models for alert queries.

This module contains Pydantic models for validating and structuring
filter parameters used in alert queries.
"""

from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar('T')


class PaginatedAlertResponse(BaseModel, Generic[T]):
    """Generic response model for paginated alert data."""
    
    items: List[T]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")


class DeviceAlertFilters(BaseModel):
    """
    Model for device alert filter parameters.
    
    This model encapsulates all possible filter criteria for device alert queries.
    """
    
    session_id: Optional[int] = Field(None, description="Filter by exact session ID")
    device_id: Optional[str] = Field(None, description="Filter by device ID (partial match)")
    reason_contains: Optional[str] = Field(None, description="Filter by reason containing this text")
    
    search: Optional[str] = Field(None, description="Generic search (ID, device, reason)")
    
    def has_filters(self) -> bool:
        """Check if any filters are set."""
        return any([
            self.session_id is not None,
            self.device_id is not None,
            self.reason_contains is not None,
            self.search is not None,
        ])


class IdentityAlertFilters(BaseModel):
    """
    Model for identity alert filter parameters.
    
    This model encapsulates all possible filter criteria for identity alert queries.
    """
    
    uid: Optional[str] = Field(None, description="Filter by UID (partial match)")
    device_id: Optional[str] = Field(None, description="Filter by device ID (partial match)")
    reason_contains: Optional[str] = Field(None, description="Filter by reason containing this text")
    min_anomaly_count: Optional[int] = Field(None, ge=0, description="Minimum repeated anomaly count")
    max_anomaly_count: Optional[int] = Field(None, ge=0, description="Maximum repeated anomaly count")
    
    search: Optional[str] = Field(None, description="Generic search (ID, UID, device, reason)")
    
    def has_filters(self) -> bool:
        """Check if any filters are set."""
        return any([
            self.uid is not None,
            self.device_id is not None,
            self.reason_contains is not None,
            self.min_anomaly_count is not None,
            self.max_anomaly_count is not None,
            self.search is not None,
        ])


class TimestampAlertFilters(BaseModel):
    """
    Model for timestamp alert filter parameters.
    
    This model encapsulates all possible filter criteria for timestamp alert queries.
    """
    
    uid: Optional[str] = Field(None, description="Filter by UID (partial match)")
    session_id: Optional[int] = Field(None, description="Filter by exact session ID")
    device_id: Optional[str] = Field(None, description="Filter by device ID (partial match)")
    reason_contains: Optional[str] = Field(None, description="Filter by reason containing this text")
    
    search: Optional[str] = Field(None, description="Generic search (ID, UID, session, device, reason)")
    
    def has_filters(self) -> bool:
        """Check if any filters are set."""
        return any([
            self.uid is not None,
            self.session_id is not None,
            self.device_id is not None,
            self.reason_contains is not None,
            self.search is not None,
        ])
