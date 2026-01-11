from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional, List

from utils import JsonRepository, get_config, load_config, GroupItemDTO
from api.services import GroupService
from api.models import (
    GroupFilters,
    PaginationParams,
    SortParams,
    PaginatedGroupResponse
)
from api.constants import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    ERROR_INVALID_PAGE,
    ERROR_READING_GROUPS,
    GROUP_SORTABLE_FIELDS
)

router = APIRouter()

def get_group_service() -> GroupService:
    """Dependency injection for GroupService."""
    load_config()
    repo = JsonRepository(get_config().PATHS.GROUPS)
    return GroupService(repo)


@router.get(
    "/",
    response_model=PaginatedGroupResponse,
    summary="List Groups",
    responses={
        400: {"description": "Invalid page number"},
        500: {"description": "Internal server error"}
    }
)
def get_groups(
    group_name: Optional[str] = Query(None, description="Filter by group name (partial match)"),
    member_uid: Optional[str] = Query(None, description="Filter by member UID present in group"),
    min_members: Optional[int] = Query(None, ge=0, description="Minimum number of members in group"),
    max_members: Optional[int] = Query(None, ge=0, description="Maximum number of members in group"),
    page: int = Query(DEFAULT_PAGE, ge=1, description="Page number"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
    order_by: Optional[str] = Query(None, description=f"Sort field: {', '.join(GROUP_SORTABLE_FIELDS)}"),
    order_direction: str = Query("asc", pattern="^(asc|desc)$"),
    service: GroupService = Depends(get_group_service)
):
    """
    Get groups with pagination, filtering, and sorting support.
    
    This endpoint retrieves all student groups with optional filtering by name,
    member UID, or size, and supports sorting and pagination.
    """
    try:
        filters = GroupFilters(
            group_name=group_name,
            member_uid=member_uid,
            min_members=min_members,
            max_members=max_members
        )
        pagination = PaginationParams(page=page, page_size=page_size)
        sort_params = SortParams(order_by=order_by, order_direction=order_direction)
        
        items, total, total_pages = service.get_filtered_groups(filters, pagination, sort_params)
        
        if page > total_pages and total > 0:
            raise HTTPException(
                status_code=400, 
                detail=ERROR_INVALID_PAGE.format(page=page, total_pages=total_pages)
            )
            
        return PaginatedGroupResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=ERROR_READING_GROUPS.format(error=str(e))
        )
