from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from api.services.session_service import SessionService
from api.services.group_service import GroupService
from api.services.alert_service import AlertService
from api.models import SessionFilters, IdentityAlertFilters, PaginationParams, SortParams
from api.models.analytics import (
    AttendanceTrendItem, 
    EnrichedGroupItem, 
    GroupTrendItem,
    GroupAnalyticsResponse
)
from utils import logger

class AnalyticsService:
    def __init__(self, session_service: SessionService, group_service: GroupService, alert_service: AlertService):
        self.session_service = session_service
        self.group_service = group_service
        self.alert_service = alert_service

    def _get_session_date(self, session: Any) -> str:
        """Helper to get a YYYY-MM-DD string from a session."""
        if hasattr(session, 'received_at') and session.received_at:
            return session.received_at.strftime("%Y-%m-%d")
        if hasattr(session, 'logs_date') and session.logs_date:
            return str(session.logs_date)
        return ""

    def get_attendance_trend(self, date_from: datetime, date_to: datetime) -> List[AttendanceTrendItem]:
        try:
            filters = SessionFilters(received_at_from=date_from, received_at_to=date_to)
            all_sessions = self.session_service.get_all_sessions()
            sessions = self.session_service.filter_sessions(all_sessions, filters)
            
            # Identify all formal group members
            groups = self.group_service.get_all_groups()
            formal_members = set()
            for g in groups:
                for m in g.members:
                    formal_members.add(str(m).strip().lower())

            trend = []
            curr = date_from
            while curr <= date_to:
                date_str = curr.strftime("%Y-%m-%d")
                day_sessions = [s for s in sessions if self._get_session_date(s) == date_str]
                
                all_uids = set()
                unassigned_present = set()
                recorded_count = 0
                for s in day_sessions:
                    recorded_count += getattr(s, 'recorded_count', 0) or 0
                    logs = getattr(s, 'logs', []) or []
                    for l in logs:
                        uid_norm = str(l.uid).strip().lower() if hasattr(l, 'uid') and l.uid else None
                        if uid_norm:
                            all_uids.add(uid_norm)
                            if uid_norm not in formal_members:
                                unassigned_present.add(uid_norm)

                display_name = curr.strftime("%m/%d")
                if date_from.year != date_to.year:
                    display_name = curr.strftime("%m/%d/%Y")

                trend.append(AttendanceTrendItem(
                    name=display_name,
                    fullDate=date_str,
                    attendance=len(all_uids),
                    unassigned=len(unassigned_present),
                    recorded=recorded_count,
                    sessions=len(day_sessions)
                ))
                curr += timedelta(days=1)
            
            return trend
        except Exception as e:
            logger.error(f"Error calculating attendance trend: {e}")
            return []

    def get_group_analytics(self, date_from: datetime, date_to: datetime) -> GroupAnalyticsResponse:
        try:
            # 1. Fetch data
            session_filters = SessionFilters(received_at_from=date_from, received_at_to=date_to)
            all_sessions = self.session_service.get_all_sessions()
            sessions = self.session_service.filter_sessions(all_sessions, session_filters)
            groups_dto = self.group_service.get_all_groups()
            
            # Enrich groups with their individual attendance trends
            enriched_groups = []
            for g in groups_dto:
                member_set = {str(m).strip().lower() for m in g.members}
                trend = []
                
                # Individual group trend (last 10 sessions)
                group_sessions = sorted(sessions, key=lambda x: self._get_session_date(x) or "", reverse=True)[:10]
                for s in reversed(group_sessions):
                    logs = getattr(s, 'logs', []) or []
                    uids_in_s = {str(l.uid).strip().lower() for l in logs if hasattr(l, 'uid') and l.uid}
                    present_count = len(uids_in_s.intersection(member_set))
                    presence_pct = round((present_count / len(g.members)) * 100) if g.members else 0
                    trend.append(GroupTrendItem(date=self._get_session_date(s), presence=presence_pct))
                
                # Overall average: unique members across ALL sessions in range
                all_uids_in_range = set()
                for s in sessions:
                    logs = getattr(s, 'logs', []) or []
                    for l in logs:
                        if hasattr(l, 'uid') and l.uid:
                            all_uids_in_range.add(str(l.uid).strip().lower())
                
                present_in_range = all_uids_in_range.intersection(member_set)
                avg = round((len(present_in_range) / len(g.members)) * 100) if g.members else 0

                enriched_groups.append(EnrichedGroupItem(
                    name=g.name,
                    members=g.members,
                    member_count=len(g.members),
                    attendanceTrend=trend,
                    avgAttendance=avg
                ))

            # 2. Multi Trend Data (Strictly Groups)
            # Generate all dates in the requested range
            all_dates = []
            curr = date_from
            while curr <= date_to:
                all_dates.append(curr.strftime("%Y-%m-%d"))
                curr += timedelta(days=1)

            multi_trend = []
            for date in all_dates:
                day_sessions = [s for s in sessions if self._get_session_date(s) == date]
                row = {"date": date}
                
                uids_on_day = set()
                for s in day_sessions:
                    logs = getattr(s, 'logs', []) or []
                    for l in logs:
                        if hasattr(l, 'uid') and l.uid:
                            uids_on_day.add(str(l.uid).strip().lower())

                for g in groups_dto:
                    member_set = {str(m).strip().lower() for m in g.members}
                    present_on_day = uids_on_day.intersection(member_set)
                    row[g.name] = round((len(present_on_day) / len(g.members)) * 100) if g.members else 0

                multi_trend.append(row)

            # 3. Colors
            colors = ['#10b981','#3b82f6','#f59e0b','#8b5cf6','#06b6d4','#ec4899','#f97316']
            group_colors = {}
            for i, g in enumerate(groups_dto):
                group_colors[g.name] = colors[i % len(colors)]

            return GroupAnalyticsResponse(
                groups=enriched_groups,
                multiTrendData=multi_trend,
                groupColors=group_colors
            )
        except Exception as e:
            logger.error(f"Error calculating group analytics: {e}", exc_info=True)
            return GroupAnalyticsResponse(groups=[], multiTrendData=[], groupColors={})

    def _get_session_date(self, session: Any) -> str:
        received_at = getattr(session, 'received_at', None)
        if not received_at:
            return ""
        if isinstance(received_at, datetime):
            return received_at.strftime("%Y-%m-%d")
        return str(received_at).split(' ')[0]
