"""
Session service for business logic.

This module contains the SessionService class which handles all business
logic related to session data retrieval, filtering, sorting, and pagination.
"""

from typing import List, Optional, Tuple
from datetime import datetime

from utils import JsonRepository, SessionDTO, logger, map_to_session_dtos
from api.models import SessionFilters, PaginationParams, SortParams
from api.constants import SORTABLE_FIELDS
from api.exceptions import (
    SessionNotFoundError,
    InvalidSortFieldError,
    InvalidDateFormatError
)


class SessionService:
    """
    Service class for session-related business logic.
    
    This class encapsulates all business logic for working with session data,
    including data retrieval, filtering, sorting, and pagination.
    """
    
    def __init__(self, repository: JsonRepository):
        """
        Initialize the SessionService.
        
        Args:
            repository: JsonRepository instance for data access
        """
        self.repository = repository
    
    def get_all_sessions(self) -> List[SessionDTO]:
        """
        Retrieve all sessions from the repository.
        
        Returns:
            List of SessionDTO instances
            
        Raises:
            SessionNotFoundError: If the data file is not found
        """
        try:
            logger.info("Loading all sessions from repository")
            raw_data = self.repository.read_all()
            sessions = map_to_session_dtos(raw_data)
            logger.info(f"Loaded {len(sessions)} sessions successfully")
            return sessions
        except FileNotFoundError as e:
            logger.warning(f"Session data file not found: {e}")
            raise SessionNotFoundError("Session data file not found") from e
    
    def filter_sessions(
        self,
        sessions: List[SessionDTO],
        filters: SessionFilters
    ) -> List[SessionDTO]:
        """
        Apply filters to a list of sessions.
        
        Args:
            sessions: List of SessionDTO instances to filter
            filters: SessionFilters instance containing filter criteria
            
        Returns:
            Filtered list of SessionDTO instances
        """
        if not filters.has_filters():
            logger.debug("No filters applied, returning all sessions")
            return sessions
        
        logger.info(f"Applying filters to {len(sessions)} sessions")
        filtered = []
        
        for session in sessions:
            # Exact match filters
            if filters.session_id is not None and session.session_id != filters.session_id:
                continue
            
            if filters.device_id is not None and session.device_id != filters.device_id:
                continue
            
            if filters.logs_date is not None and session.logs_date != filters.logs_date:
                continue
            
            # Date range filters
            if filters.received_at_from is not None:
                if session.received_at is None or session.received_at < filters.received_at_from:
                    continue
            
            if filters.received_at_to is not None:
                if session.received_at is None or session.received_at > filters.received_at_to:
                    continue
            
            # Count range filters
            if filters.recorded_count_min is not None:
                if session.recorded_count is None or session.recorded_count < filters.recorded_count_min:
                    continue
            
            if filters.recorded_count_max is not None:
                if session.recorded_count is None or session.recorded_count > filters.recorded_count_max:
                    continue
            
            if filters.unique_count_min is not None:
                if session.unique_count is None or session.unique_count < filters.unique_count_min:
                    continue
            
            if filters.unique_count_max is not None:
                if session.unique_count is None or session.unique_count > filters.unique_count_max:
                    continue
            
            # Text search filter
            if filters.session_context_contains is not None:
                if session.session_context is None:
                    continue
                if filters.session_context_contains.lower() not in session.session_context.lower():
                    continue
            
            # If all filters pass, add to results
            filtered.append(session)
        
        logger.info(f"Filtered to {len(filtered)} sessions")
        return filtered
    
    def sort_sessions(
        self,
        sessions: List[SessionDTO],
        sort_params: SortParams
    ) -> List[SessionDTO]:
        """
        Sort sessions by the specified field and direction.
        
        Args:
            sessions: List of SessionDTO instances to sort
            sort_params: SortParams instance containing sort criteria
            
        Returns:
            Sorted list of SessionDTO instances
            
        Raises:
            InvalidSortFieldError: If the sort field is not valid
        """
        if sort_params.order_by is None:
            logger.debug("No sorting applied")
            return sessions
        
        # Validate sort field
        if sort_params.order_by not in SORTABLE_FIELDS:
            raise InvalidSortFieldError(sort_params.order_by, SORTABLE_FIELDS)
        
        logger.info(f"Sorting sessions by {sort_params.order_by} ({sort_params.order_direction})")
        
        reverse = sort_params.is_descending()
        
        # Sort with None-safe key function
        def sort_key(session: SessionDTO) -> Tuple:
            value = getattr(session, sort_params.order_by)
            # Handle None values by placing them at the end
            if value is None:
                return (1, None) if not reverse else (0, None)
            return (0, value) if not reverse else (1, value)
        
        sorted_sessions = sorted(sessions, key=sort_key, reverse=reverse)
        return sorted_sessions
    
    def paginate_sessions(
        self,
        sessions: List[SessionDTO],
        pagination: PaginationParams
    ) -> Tuple[List[SessionDTO], int]:
        """
        Apply pagination to sessions.
        
        Args:
            sessions: List of SessionDTO instances to paginate
            pagination: PaginationParams instance containing pagination settings
            
        Returns:
            Tuple of (paginated sessions, total pages)
        """
        total = len(sessions)
        total_pages = max(1, (total + pagination.page_size - 1) // pagination.page_size)
        
        logger.info(f"Paginating {total} sessions: page {pagination.page} of {total_pages}")
        
        # Get slice indices
        start_idx, end_idx = pagination.get_slice_indices()
        
        # Apply pagination
        paginated = sessions[start_idx:end_idx]
        
        return paginated, total_pages
    
    def get_sessions_with_pagination(
        self,
        pagination: PaginationParams,
        sort_params: SortParams
    ) -> Tuple[List[SessionDTO], int, int]:
        """
        Get all sessions with sorting and pagination applied.
        
        Args:
            pagination: PaginationParams instance
            sort_params: SortParams instance
            
        Returns:
            Tuple of (paginated sessions, total count, total pages)
        """
        # Load all sessions
        sessions = self.get_all_sessions()
        
        # Apply sorting
        sorted_sessions = self.sort_sessions(sessions, sort_params)
        
        # Apply pagination
        paginated, total_pages = self.paginate_sessions(sorted_sessions, pagination)
        
        return paginated, len(sessions), total_pages
    
    def get_filtered_sessions_with_pagination(
        self,
        filters: SessionFilters,
        pagination: PaginationParams,
        sort_params: SortParams
    ) -> Tuple[List[SessionDTO], int, int]:
        """
        Get filtered sessions with sorting and pagination applied.
        
        Args:
            filters: SessionFilters instance
            pagination: PaginationParams instance
            sort_params: SortParams instance
            
        Returns:
            Tuple of (paginated sessions, total count, total pages)
        """
        # Load all sessions
        sessions = self.get_all_sessions()
        
        # Apply filters
        filtered_sessions = self.filter_sessions(sessions, filters)
        
        # Apply sorting
        sorted_sessions = self.sort_sessions(filtered_sessions, sort_params)
        
        # Apply pagination
        paginated, total_pages = self.paginate_sessions(sorted_sessions, pagination)
        
        return paginated, len(filtered_sessions), total_pages
