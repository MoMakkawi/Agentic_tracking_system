from fastapi import APIRouter, Depends, Query
from datetime import datetime
from typing import List

from api.services.analytics_service import AnalyticsService
from api.services.session_service import SessionService
from api.services.group_service import GroupService
from api.services.alert_service import AlertService
from api.models.analytics import GroupAnalyticsResponse, AttendanceTrendItem
from api.routers.attendance import get_session_service
from api.routers.groups import get_group_service
from api.routers.alerts import get_identity_alert_service

router = APIRouter()

def get_analytics_service(
    session_service: SessionService = Depends(get_session_service),
    group_service: GroupService = Depends(get_group_service),
    alert_service: AlertService = Depends(get_identity_alert_service)
) -> AnalyticsService:
    return AnalyticsService(session_service, group_service, alert_service)

@router.get("/groups", response_model=GroupAnalyticsResponse)
async def get_group_analytics(
    received_at_from: str = Query(..., description="Start date (YYYY-MM-DD)"),
    received_at_to: str = Query(..., description="End date (YYYY-MM-DD)"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    dt_from = datetime.strptime(received_at_from, "%Y-%m-%d")
    dt_to = datetime.strptime(received_at_to, "%Y-%m-%d")
    dt_to = dt_to.replace(hour=23, minute=59, second=59)
    return service.get_group_analytics(dt_from, dt_to)

@router.get("/attendance-trend", response_model=List[AttendanceTrendItem])
async def get_attendance_trend(
    received_at_from: str = Query(..., description="Start date (YYYY-MM-DD)"),
    received_at_to: str = Query(..., description="End date (YYYY-MM-DD)"),
    service: AnalyticsService = Depends(get_analytics_service)
):
    dt_from = datetime.strptime(received_at_from, "%Y-%m-%d")
    dt_to = datetime.strptime(received_at_to, "%Y-%m-%d")
    dt_to = dt_to.replace(hour=23, minute=59, second=59)
    return service.get_attendance_trend(dt_from, dt_to)
