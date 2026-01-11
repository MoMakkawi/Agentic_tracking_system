"""
Alert service for business logic.

This module contains the AlertService class which handles all business
logic related to alert data retrieval, filtering, sorting, and pagination.
"""

from typing import List, Optional, Tuple, TypeVar, Any, Callable
from utils import CsvRepository
from utils import (
    DeviceAlertDTO, IdentityAlertDTO, TimestampAlertDTO,
    map_to_device_alert_dto, map_to_identity_alert_dto, map_to_timestamp_alert_dto
)
from api.models import (
    DeviceAlertFilters,
    IdentityAlertFilters,
    TimestampAlertFilters,
    PaginationParams,
    SortParams
)
from api.constants import (
    DEVICE_ALERT_SORTABLE_FIELDS,
    IDENTITY_ALERT_SORTABLE_FIELDS,
    TIMESTAMP_ALERT_SORTABLE_FIELDS
)

T = TypeVar('T')


class AlertService:
    """
    Service class for alert-related business logic.
    """
    
    def __init__(self, repository: CsvRepository):
        self.repository = repository

    def _paginate(self, items: List[T], pagination: PaginationParams) -> Tuple[List[T], int]:
        total = len(items)
        total_pages = max(1, (total + pagination.page_size - 1) // pagination.page_size)
        start_idx, end_idx = pagination.get_slice_indices()
        return items[start_idx:end_idx], total_pages

    def _sort(self, items: List[T], sort_params: SortParams, sortable_fields: List[str]) -> List[T]:
        if sort_params.order_by is None:
            return items
        
        if sort_params.order_by not in sortable_fields:
            # Fallback to no sorting if invalid field requested (or maybe raise?)
            return items
        
        reverse = sort_params.is_descending()
        
        def sort_key(item: Any) -> Tuple:
            value = getattr(item, sort_params.order_by)
            if value is None:
                return (1, None) if not reverse else (0, None)
            return (0, value) if not reverse else (1, value)
            
        return sorted(items, key=sort_key, reverse=reverse)

    def get_device_alerts(
        self,
        filters: DeviceAlertFilters,
        pagination: PaginationParams,
        sort_params: SortParams
    ) -> Tuple[List[DeviceAlertDTO], int, int]:
        try:
            raw_data = self.repository.read_all()
            alerts = [map_to_device_alert_dto(item) for item in raw_data]
            
            # Filtering
            filtered = []
            
            for alert in alerts:
                if filters.session_id is not None and alert.session_id != filters.session_id:
                    continue
                if filters.device_id is not None and filters.device_id.lower() not in alert.device_id.lower():
                    continue
                if filters.reason_contains is not None:
                    found = any(filters.reason_contains.lower() in r.lower() for r in alert.reasons)
                    if not found:
                        continue
                
                # Generic search
                if filters.search is not None:
                    s_term = filters.search.lower()
                    # Check ID, Session ID, Device ID, or Reasons
                    found_search = (
                        s_term in str(alert.id) or
                        s_term in str(alert.session_id) or
                        s_term in alert.device_id.lower() or
                        any(s_term in r.lower() for r in alert.reasons)
                    )
                    if not found_search:
                        continue
                
                filtered.append(alert)
                
            sorted_alerts = self._sort(filtered, sort_params, DEVICE_ALERT_SORTABLE_FIELDS)
            paginated, total_pages = self._paginate(sorted_alerts, pagination)
            
            return paginated, len(filtered), total_pages
        except FileNotFoundError:
            return [], 0, 1

    def get_identity_alerts(
        self,
        filters: IdentityAlertFilters,
        pagination: PaginationParams,
        sort_params: SortParams
    ) -> Tuple[List[IdentityAlertDTO], int, int]:
        try:
            raw_data = self.repository.read_all()
            alerts = [map_to_identity_alert_dto(item) for item in raw_data]
            
            # Filtering
            filtered = []
            
            for alert in alerts:
                if filters.uid is not None and filters.uid.lower() not in alert.uid.lower():
                    continue
                if filters.device_id is not None and filters.device_id.lower() not in alert.device_id.lower():
                    continue
                if filters.reason_contains is not None:
                    found = any(filters.reason_contains.lower() in r.lower() for r in alert.reasons)
                    if not found:
                        continue
                
                # Generic search
                if filters.search is not None:
                    s_term = filters.search.lower()
                    # Check ID, UID, Device ID, Reasons, or Anomaly Sessions
                    found_search = (
                        s_term in str(alert.id) or
                        s_term in alert.uid.lower() or
                        s_term in alert.device_id.lower() or
                        any(s_term in r.lower() for r in alert.reasons) or
                        (alert.anomaly_sessions and any(s_term in str(s) for s in alert.anomaly_sessions))
                    )
                    if not found_search:
                        continue
                if filters.min_anomaly_count is not None and alert.repeated_anomaly_count < filters.min_anomaly_count:
                    continue
                if filters.max_anomaly_count is not None and alert.repeated_anomaly_count > filters.max_anomaly_count:
                    continue
                
                filtered.append(alert)
                
            sorted_alerts = self._sort(filtered, sort_params, IDENTITY_ALERT_SORTABLE_FIELDS)
            paginated, total_pages = self._paginate(sorted_alerts, pagination)
            
            return paginated, len(filtered), total_pages
        except FileNotFoundError:
            return [], 0, 1

    def get_timestamp_alerts(
        self,
        filters: TimestampAlertFilters,
        pagination: PaginationParams,
        sort_params: SortParams
    ) -> Tuple[List[TimestampAlertDTO], int, int]:
        try:
            raw_data = self.repository.read_all()
            alerts = [map_to_timestamp_alert_dto(item) for item in raw_data]
            
            # Filtering
            filtered = []
            
            for alert in alerts:
                if filters.uid is not None and filters.uid.lower() not in alert.uid.lower():
                    continue
                if filters.session_id is not None and alert.session_id != filters.session_id:
                    continue
                if filters.device_id is not None and filters.device_id.lower() not in alert.device_id.lower():
                    continue
                if filters.reason_contains is not None:
                    found = any(filters.reason_contains.lower() in r.lower() for r in alert.reasons)
                    if not found:
                        continue
                
                # Generic search
                if filters.search is not None:
                    s_term = filters.search.lower()
                    # Check ID, UID, Session ID, Device ID, or Reasons
                    found_search = (
                        s_term in str(alert.id) or
                        s_term in alert.uid.lower() or
                        s_term in str(alert.session_id) or
                        s_term in alert.device_id.lower() or
                        any(s_term in r.lower() for r in alert.reasons)
                    )
                    if not found_search:
                        continue
                
                filtered.append(alert)
                
            sorted_alerts = self._sort(filtered, sort_params, TIMESTAMP_ALERT_SORTABLE_FIELDS)
            paginated, total_pages = self._paginate(sorted_alerts, pagination)
            
            return paginated, len(filtered), total_pages
        except FileNotFoundError:
            return [], 0, 1
