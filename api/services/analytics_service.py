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
from utils import logger, get_config

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

    def _is_late(self, log_ts: str, session_start: str, lateness_threshold_minutes: int) -> bool:
        """Return True if log_ts is >= lateness_threshold_minutes after session_start."""
        try:
            # ts is HH:MM or HH:MM:SS, session_start is a full ISO datetime string
            ref = datetime.fromisoformat(session_start)
            ref_minutes = ref.hour * 60 + ref.minute
            parts = log_ts.split(':')
            log_minutes = int(parts[0]) * 60 + int(parts[1])
            return (log_minutes - ref_minutes) > lateness_threshold_minutes
        except Exception:
            return False

    def get_group_analytics(self, date_from: datetime, date_to: datetime) -> GroupAnalyticsResponse:
        try:
            # Load analytics config thresholds
            try:
                cfg = get_config()
                analytics_cfg = cfg.ANALYTICS
                lateness_threshold = analytics_cfg.LATENESS_THRESHOLD_MINUTES
                min_missed = analytics_cfg.MIN_MISSED_SESSIONS
                min_late = analytics_cfg.MIN_LATE_SESSIONS
            except Exception:
                lateness_threshold = 10
                min_missed = 1
                min_late = 1

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

                # --- Attendance bucket computation ---
                # For each member, track: attended_sessions, missed_sessions, late_sessions
                member_attended = {m: 0 for m in member_set}   # sessions they appeared in
                member_late = {m: 0 for m in member_set}       # sessions they were late in

                for s in sessions:
                    logs = getattr(s, 'logs', []) or []
                    # Get session start reference time from matched_sessions if available
                    matched = getattr(s, 'matched_sessions', []) or []
                    session_start = None
                    if matched:
                        ms0 = matched[0]
                        session_start = getattr(ms0, 'start', None)
                        if session_start and not isinstance(session_start, str):
                            try:
                                session_start = session_start.isoformat()
                            except Exception:
                                session_start = str(session_start)

                    # Build uid -> first ts mapping for members in this session
                    uid_first_ts: Dict[str, str] = {}
                    for l in logs:
                        uid_norm = str(l.uid).strip().lower() if hasattr(l, 'uid') and l.uid else None
                        ts = str(getattr(l, 'ts', '') or '')
                        if uid_norm and uid_norm in member_set:
                            if uid_norm not in uid_first_ts:
                                uid_first_ts[uid_norm] = ts

                    # Use first log as fallback reference if no matched session
                    first_log_ts = next(iter(uid_first_ts.values()), None) if uid_first_ts else None

                    for member in member_set:
                        if member in uid_first_ts:
                            member_attended[member] += 1
                            ts = uid_first_ts[member]
                            # Determine reference time for lateness check
                            if session_start:
                                is_late = self._is_late(ts, session_start, lateness_threshold)
                            elif first_log_ts and first_log_ts != ts:
                                # Use first log as reference only when no start time available
                                try:
                                    ref_parts = first_log_ts.split(':')
                                    ref_min = int(ref_parts[0]) * 60 + int(ref_parts[1])
                                    mem_parts = ts.split(':')
                                    mem_min = int(mem_parts[0]) * 60 + int(mem_parts[1])
                                    is_late = (mem_min - ref_min) > lateness_threshold
                                except Exception:
                                    is_late = False
                            else:
                                is_late = False
                            if is_late:
                                member_late[member] += 1

                # Count sessions relevant to this group (where at least one member was present)
                group_relevant_sessions = sum(
                    1 for s in sessions
                    if any(
                        str(l.uid).strip().lower() in member_set
                        for l in (getattr(s, 'logs', []) or [])
                        if hasattr(l, 'uid') and l.uid
                    )
                )

                # Categorize each member into one of the four buckets
                did_not_attend_at_all = 0
                did_not_attend_sometimes = 0
                late_count = 0
                on_time_count = 0

                for member in member_set:
                    attended = member_attended[member]
                    missed = group_relevant_sessions - attended
                    late_sess = member_late[member]

                    if attended == 0:
                        did_not_attend_at_all += 1
                    elif missed >= min_missed:
                        did_not_attend_sometimes += 1
                    elif late_sess >= min_late:
                        late_count += 1
                    else:
                        on_time_count += 1

                enriched_groups.append(EnrichedGroupItem(
                    name=g.name,
                    members=g.members,
                    member_count=len(g.members),
                    attendanceTrend=trend,
                    avgAttendance=avg,
                    did_not_attend_at_all=did_not_attend_at_all,
                    did_not_attend_sometimes=did_not_attend_sometimes,
                    late=late_count,
                    on_time=on_time_count
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

