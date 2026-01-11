"""
Attendance router for session-related endpoints.

This module provides REST API endpoints for retrieving, filtering,
and paginating attendance session data.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from utils import JsonRepository, CsvRepository, SessionDTO, get_config, load_config, logger
from api.services import SessionService
from api.models import SessionFilters, PaginationParams, SortParams
from api.constants import (
    SORTABLE_FIELDS,
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    ERROR_INVALID_PAGE,
    ERROR_READING_SESSIONS,
    ERROR_FILTERING_SESSIONS
)
from api.exceptions import (
    SessionNotFoundError,
    InvalidSortFieldError,
    InvalidDateFormatError
)

router = APIRouter()


class PaginatedResponse(BaseModel):
    """Response model for paginated data."""
    
    model_config = {"arbitrary_types_allowed": True}
    
    items: List[SessionDTO]
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    page_size: int = Field(description="Number of items per page")
    total_pages: int = Field(description="Total number of pages")


def get_session_service() -> SessionService:
    """
    Dependency injection for SessionService.
    
    Returns:
        SessionService instance configured with the appropriate repository and alert repos
    """
    load_config()
    conf = get_config()
    repo = JsonRepository(conf.PATHS.PREPROCESSED)
    
    # Initialize alert repositories for aggregation
    alert_repos = {
        'timestamp': CsvRepository(conf.PATHS.ALERTS.VALIDATION.TIMESTAMP),
        'identity': CsvRepository(conf.PATHS.ALERTS.VALIDATION.IDENTITY),
        'device': CsvRepository(conf.PATHS.ALERTS.VALIDATION.DEVICE)
    }
    
    return SessionService(repo, alert_repos=alert_repos)


def parse_date_filter(value: Optional[str], field_name: str, end_of_day: bool = False) -> Optional[datetime]:
    """
    Parse a date filter value from string to datetime.
    
    Args:
        value: The date string to parse
        field_name: Name of the field (for error messages)
        end_of_day: If True and only date is provided, set time to 23:59:59
        
    Returns:
        Parsed datetime or None
        
    Raises:
        HTTPException: If the date format is invalid
    """
    if value is None:
        return None
    
    try:
        dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        # Set to end of day if only date is provided
        if end_of_day and len(value) == 10:  # YYYY-MM-DD format
            dt = dt.replace(hour=23, minute=59, second=59)
        return dt
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} format: {value}. Expected ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)"
        )


@router.get(
    "/",
    response_model=PaginatedResponse,
    summary="List Attendance Sessions",
    description="Retrieve a paginated list of attendance sessions with optional sorting.",
    responses={
        400: {"description": "Invalid page number or sort parameter"},
        500: {"description": "Internal server error"}
    }
)
def get_sessions(
    page: int = Query(DEFAULT_PAGE, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Number of items per page"),
    order_by: Optional[str] = Query(
        None,
        description=f"Field to order by ({', '.join(SORTABLE_FIELDS)})"
    ),
    order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Order direction: asc or desc"),
    service: SessionService = Depends(get_session_service)
):
    """
    Get sessions with pagination, ordering support, and optional group filtering.
    
    This endpoint retrieves all attendance sessions with optional sorting
    and pagination applied.
    
    **Query Parameters:**
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (1-100)
    - **order_by**: Field to sort by (optional)
    - **order_direction**: Sort direction - 'asc' or 'desc' (default: 'asc')
    
    **Returns:**
    Paginated response containing session items and pagination metadata.
    """
    try:
        # Create parameter objects
        pagination = PaginationParams(page=page, page_size=page_size)
        sort_params = SortParams(order_by=order_by, order_direction=order_direction)
        
        # Get sessions from service
        sessions, total, total_pages = service.get_sessions_with_pagination(
            pagination=pagination,
            sort_params=sort_params
        )
        
        # Validate page number
        if page > total_pages and total > 0:
            raise HTTPException(
                status_code=400,
                detail=ERROR_INVALID_PAGE.format(page=page, total_pages=total_pages)
            )
        
        return PaginatedResponse(
            items=sessions,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except SessionNotFoundError:
        # Return empty paginated response if no data exists
        logger.info("No session data found, returning empty response")
        return PaginatedResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=1
        )
    except InvalidSortFieldError as e:
        logger.warning(f"Invalid sort field requested: {e.field}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ERROR_READING_SESSIONS.format(error=str(e))
        )


@router.get(
    "/filter",
    response_model=PaginatedResponse,
    summary="Filter Attendance Sessions",
    description="Search and filter attendance sessions using multiple criteria including date ranges, exact matches, and text search.",
    responses={
        400: {"description": "Invalid filter format or page number"},
        500: {"description": "Internal server error"}
    }
)
def filter_sessions(
    # Exact match filters
    session_id: Optional[int] = Query(None, description="Filter by exact session ID"),
    device_id: Optional[str] = Query(None, description="Filter by exact device ID"),
    logs_date: Optional[str] = Query(None, description="Filter by exact logs date (YYYY-MM-DD)"),
    
    # Range filters for dates
    received_at_from: Optional[str] = Query(None, description="Filter sessions received from this date (YYYY-MM-DD or ISO format)"),
    received_at_to: Optional[str] = Query(None, description="Filter sessions received until this date (YYYY-MM-DD or ISO format)"),
    
    # Range filters for counts
    recorded_count_min: Optional[int] = Query(None, ge=0, description="Minimum recorded count"),
    recorded_count_max: Optional[int] = Query(None, ge=0, description="Maximum recorded count"),
    unique_count_min: Optional[int] = Query(None, ge=0, description="Minimum unique count"),
    unique_count_max: Optional[int] = Query(None, ge=0, description="Maximum unique count"),
    
    # Text search
    session_context_contains: Optional[str] = Query(None, description="Filter by session context containing this text (case-insensitive)"),
    search: Optional[str] = Query(None, description="Generic search term impacting multiple fields"),
    
    # Boolean toggles
    has_alerts: Optional[bool] = Query(None, description="Filter sessions that have at least one alert"),
    
    # Pagination and ordering
    page: int = Query(DEFAULT_PAGE, ge=1, description="Page number (starts from 1)"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Number of items per page"),
    order_by: Optional[str] = Query(
        None,
        description=f"Field to order by ({', '.join(SORTABLE_FIELDS)})"
    ),
    order_direction: str = Query("asc", pattern="^(asc|desc)$", description="Order direction: asc or desc"),
    service: SessionService = Depends(get_session_service)
):
    """
    Filter sessions with multiple criteria, pagination, and ordering support.
    
    This endpoint provides comprehensive filtering capabilities for attendance
    sessions, including exact matches, range filters, and text search.
    
    **Exact Match Filters:**
    - **session_id**: Filter by exact session ID
    - **device_id**: Filter by exact device ID
    - **logs_date**: Filter by exact logs date (YYYY-MM-DD)
    
    **Range Filters:**
    - **received_at_from/to**: Filter by received date range
    - **recorded_count_min/max**: Filter by recorded count range
    - **unique_count_min/max**: Filter by unique count range
    
    **Text Search:**
    - **session_context_contains**: Search for text in session context (case-insensitive)
    - **search**: Generic search term impacting multiple fields
    
    **Pagination & Ordering:**
    - **page**: Page number (starts from 1)
    - **page_size**: Number of items per page (1-100)
    - **order_by**: Field to sort by (optional)
    - **order_direction**: Sort direction - 'asc' or 'desc' (default: 'asc')
    
    **Returns:**
    Paginated response containing filtered session items and pagination metadata.
    """
    try:
        # Parse date filters
        received_from_dt = parse_date_filter(received_at_from, "received_at_from")
        received_to_dt = parse_date_filter(received_at_to, "received_at_to", end_of_day=True)
        
        # Create filter object
        filters = SessionFilters(
            session_id=session_id,
            device_id=device_id,
            logs_date=logs_date,
            received_at_from=received_from_dt,
            received_at_to=received_to_dt,
            recorded_count_min=recorded_count_min,
            recorded_count_max=recorded_count_max,
            unique_count_min=unique_count_min,
            unique_count_max=unique_count_max,
            session_context_contains=session_context_contains,
            search=search,
            has_alerts=has_alerts
        )
        
        # Create parameter objects
        pagination = PaginationParams(page=page, page_size=page_size)
        sort_params = SortParams(order_by=order_by, order_direction=order_direction)
        
        # Get filtered sessions from service
        sessions, total, total_pages = service.get_filtered_sessions_with_pagination(
            filters=filters,
            pagination=pagination,
            sort_params=sort_params
        )
        
        # Validate page number
        if page > total_pages and total > 0:
            raise HTTPException(
                status_code=400,
                detail=ERROR_INVALID_PAGE.format(page=page, total_pages=total_pages)
            )
        
        return PaginatedResponse(
            items=sessions,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
        
    except SessionNotFoundError:
        # Return empty paginated response if no data exists
        logger.info("No session data found, returning empty response")
        return PaginatedResponse(
            items=[],
            total=0,
            page=page,
            page_size=page_size,
            total_pages=1
        )
    except InvalidSortFieldError as e:
        logger.warning(f"Invalid sort field requested: {e.field}")
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error in filter_sessions: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=ERROR_FILTERING_SESSIONS.format(error=str(e))
        )


@router.get(
    "/stats", 
    summary="Get Session Statistics",
    description="Get summary statistics for all attendance sessions, including total count and sessions with alerts.",
    responses={
        500: {"description": "Internal server error"}
    }
)
def get_session_stats(service: SessionService = Depends(get_session_service)):
    """
    Get summary statistics for attendance sessions.
    
    Returns:
        JSON object with total counts and alert counts.
    """
    try:
        sessions = service.get_all_sessions()
        total = len(sessions)
        with_alerts = len([s for s in sessions if s.alert_count > 0])
        
        return {
            "total": total,
            "with_alerts": with_alerts
        }
    except Exception as e:
        logger.error(f"Error getting session stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
