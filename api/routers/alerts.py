from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional

from utils import get_config, load_config, logger, CsvRepository
from utils import DeviceAlertDTO, IdentityAlertDTO, TimestampAlertDTO
from api.services import AlertService
from api.models import (
    PaginatedAlertResponse,
    DeviceAlertFilters,
    IdentityAlertFilters,
    TimestampAlertFilters,
    PaginationParams,
    SortParams
)
from api.constants import (
    DEFAULT_PAGE,
    DEFAULT_PAGE_SIZE,
    MAX_PAGE_SIZE,
    ERROR_INVALID_PAGE,
    ERROR_READING_ALERTS,
    DEVICE_ALERT_SORTABLE_FIELDS,
    IDENTITY_ALERT_SORTABLE_FIELDS,
    TIMESTAMP_ALERT_SORTABLE_FIELDS
)

router = APIRouter()

def get_alert_service(path: str) -> AlertService:
    """Dependency injection for AlertService."""
    load_config()
    repo = CsvRepository(path)
    return AlertService(repo)

def get_device_alert_service() -> AlertService:
    load_config()
    return get_alert_service(get_config().PATHS.ALERTS.VALIDATION.DEVICE)

def get_identity_alert_service() -> AlertService:
    load_config()
    return get_alert_service(get_config().PATHS.ALERTS.VALIDATION.IDENTITY)

def get_timestamp_alert_service() -> AlertService:
    load_config()
    return get_alert_service(get_config().PATHS.ALERTS.VALIDATION.TIMESTAMP)


@router.get(
    "/device",
    response_model=PaginatedAlertResponse[DeviceAlertDTO],
    summary="Get Device Alerts",
    description="Retrieve a paginated list of device validation alerts.",
    responses={
        400: {"description": "Invalid page number"},
        500: {"description": "Internal server error"}
    }
)
def get_device_alerts(
    session_id: Optional[int] = Query(None, description="Filter by exact session ID"),
    device_id: Optional[str] = Query(None, description="Filter by device ID (partial match)"),
    reason_contains: Optional[str] = Query(None, description="Filter by reason containing this text"),
    search: Optional[str] = Query(None, description="Generic search across fields"),
    page: int = Query(DEFAULT_PAGE, ge=1, description="Page number"),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE, description="Items per page"),
    order_by: Optional[str] = Query(None, description=f"Sort field: {', '.join(DEVICE_ALERT_SORTABLE_FIELDS)}"),
    order_direction: str = Query("asc", pattern="^(asc|desc)$"),
    service: AlertService = Depends(get_device_alert_service)
):
    try:
        filters = DeviceAlertFilters(
            session_id=session_id,
            device_id=device_id,
            reason_contains=reason_contains,
            search=search
        )
        pagination = PaginationParams(page=page, page_size=page_size)
        sort_params = SortParams(order_by=order_by, order_direction=order_direction)
        
        items, total, total_pages = service.get_device_alerts(filters, pagination, sort_params)
        
        if page > total_pages and total > 0:
            raise HTTPException(status_code=400, detail=ERROR_INVALID_PAGE.format(page=page, total_pages=total_pages))
            
        return PaginatedAlertResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error reading device alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ERROR_READING_ALERTS.format(error=str(e)))


@router.get(
    "/identity",
    response_model=PaginatedAlertResponse[IdentityAlertDTO],
    summary="Get Identity Alerts",
    description="Retrieve a paginated list of identity validation alerts.",
    responses={
        400: {"description": "Invalid page number"},
        500: {"description": "Internal server error"}
    }
)
def get_identity_alerts(
    uid: Optional[str] = Query(None, description="Filter by UID (partial match)"),
    device_id: Optional[str] = Query(None, description="Filter by device ID (partial match)"),
    reason_contains: Optional[str] = Query(None, description="Filter by reason containing this text"),
    search: Optional[str] = Query(None, description="Generic search across fields"),
    min_anomaly_count: Optional[int] = Query(None, ge=0),
    max_anomaly_count: Optional[int] = Query(None, ge=0),
    page: int = Query(DEFAULT_PAGE, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    order_by: Optional[str] = Query(None, description=f"Sort field: {', '.join(IDENTITY_ALERT_SORTABLE_FIELDS)}"),
    order_direction: str = Query("asc", pattern="^(asc|desc)$"),
    service: AlertService = Depends(get_identity_alert_service)
):
    try:
        filters = IdentityAlertFilters(
            uid=uid,
            device_id=device_id,
            reason_contains=reason_contains,
            min_anomaly_count=min_anomaly_count,
            max_anomaly_count=max_anomaly_count,
            search=search
        )
        pagination = PaginationParams(page=page, page_size=page_size)
        sort_params = SortParams(order_by=order_by, order_direction=order_direction)
        
        items, total, total_pages = service.get_identity_alerts(filters, pagination, sort_params)
        
        if page > total_pages and total > 0:
            raise HTTPException(status_code=400, detail=ERROR_INVALID_PAGE.format(page=page, total_pages=total_pages))
            
        return PaginatedAlertResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error reading identity alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ERROR_READING_ALERTS.format(error=str(e)))


@router.get(
    "/timestamp",
    response_model=PaginatedAlertResponse[TimestampAlertDTO],
    summary="Get Timestamp Alerts",
    description="Retrieve a paginated list of timestamp validation alerts.",
    responses={
        400: {"description": "Invalid page number"},
        500: {"description": "Internal server error"}
    }
)
def get_timestamp_alerts(
    uid: Optional[str] = Query(None),
    session_id: Optional[int] = Query(None),
    device_id: Optional[str] = Query(None),
    reason_contains: Optional[str] = Query(None),
    search: Optional[str] = Query(None, description="Generic search across fields"),
    page: int = Query(DEFAULT_PAGE, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=MAX_PAGE_SIZE),
    order_by: Optional[str] = Query(None, description=f"Sort field: {', '.join(TIMESTAMP_ALERT_SORTABLE_FIELDS)}"),
    order_direction: str = Query("asc", pattern="^(asc|desc)$"),
    service: AlertService = Depends(get_timestamp_alert_service)
):
    try:
        filters = TimestampAlertFilters(
            uid=uid,
            session_id=session_id,
            device_id=device_id,
            reason_contains=reason_contains,
            search=search
        )
        pagination = PaginationParams(page=page, page_size=page_size)
        sort_params = SortParams(order_by=order_by, order_direction=order_direction)
        
        items, total, total_pages = service.get_timestamp_alerts(filters, pagination, sort_params)
        
        if page > total_pages and total > 0:
            raise HTTPException(status_code=400, detail=ERROR_INVALID_PAGE.format(page=page, total_pages=total_pages))
            
        return PaginatedAlertResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )
    except Exception as e:
        logger.error(f"Error reading timestamp alerts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=ERROR_READING_ALERTS.format(error=str(e)))
