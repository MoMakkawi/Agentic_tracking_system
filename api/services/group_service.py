"""
Group service for business logic.

This module contains the GroupService class which handles all business
logic related to student group data retrieval, filtering, sorting, and pagination.
"""

from typing import List, Tuple, Any
from utils import JsonRepository, GroupItemDTO, logger, map_to_group_item_dto
from api.models import (
    GroupFilters,
    PaginationParams,
    SortParams
)
from api.constants import GROUP_SORTABLE_FIELDS


class GroupService:
    """
    Service class for group-related business logic.
    """
    
    def __init__(self, repository: JsonRepository):
        """
        Initialize the GroupService.
        
        Args:
            repository: JsonRepository instance for data access
        """
        self.repository = repository

    def _paginate(self, items: List[GroupItemDTO], pagination: PaginationParams) -> Tuple[List[GroupItemDTO], int]:
        total = len(items)
        total_pages = max(1, (total + pagination.page_size - 1) // pagination.page_size)
        start_idx, end_idx = pagination.get_slice_indices()
        return items[start_idx:end_idx], total_pages

    def _sort(self, items: List[GroupItemDTO], sort_params: SortParams) -> List[GroupItemDTO]:
        if sort_params.order_by is None:
            return items
        
        if sort_params.order_by not in GROUP_SORTABLE_FIELDS:
            return items
        
        reverse = sort_params.is_descending()
        
        def sort_key(item: GroupItemDTO) -> Any:
            value = getattr(item, sort_params.order_by)
            if value is None:
                return (1, None) if not reverse else (0, None)
            return (0, value) if not reverse else (1, value)
            
        return sorted(items, key=sort_key, reverse=reverse)

    def get_all_groups(self) -> List[GroupItemDTO]:
        """
        Retrieve all groups and map them to DTOs.
        
        Returns:
            List of GroupItemDTO instances
        """
        try:
            data = self.repository.read_all()
            groups_data = {}
            
            # Repository might return a list containing the dict or the dict itself
            if isinstance(data, list) and len(data) > 0:
                groups_data = data[0] if isinstance(data[0], dict) else {}
            elif isinstance(data, dict):
                groups_data = data
                
            return [
                map_to_group_item_dto(name, members)
                for name, members in groups_data.items()
            ]
        except FileNotFoundError:
            logger.warning("Groups data file not found")
            return []
        except Exception as e:
            logger.error(f"Error reading groups: {e}")
            return []

    def get_filtered_groups(
        self,
        filters: GroupFilters,
        pagination: PaginationParams,
        sort_params: SortParams
    ) -> Tuple[List[GroupItemDTO], int, int]:
        """
        Get filtered groups with sorting and pagination applied.
        
        Args:
            filters: GroupFilters instance
            pagination: PaginationParams instance
            sort_params: SortParams instance
            
        Returns:
            Tuple of (paginated groups, total count, total pages)
        """
        groups = self.get_all_groups()
        
        # Filtering
        filtered = []
        for group in groups:
            if filters.group_name is not None and filters.group_name.lower() not in group.name.lower():
                continue
            
            if filters.member_uid is not None and filters.member_uid not in group.members:
                continue
                
            if filters.min_members is not None and group.member_count < filters.min_members:
                continue
                
            if filters.max_members is not None and group.member_count > filters.max_members:
                continue
                
            filtered.append(group)
            
        # Sorting
        sorted_groups = self._sort(filtered, sort_params)
        
        # Pagination
        paginated, total_pages = self._paginate(sorted_groups, pagination)
        
        return paginated, len(filtered), total_pages
