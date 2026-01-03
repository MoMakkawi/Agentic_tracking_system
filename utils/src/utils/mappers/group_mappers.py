"""
Data mappers for group-related DTOs.

This module contains functions for mapping raw dictionary data
to group Data Transfer Objects (DTOs).
"""

from typing import Dict, List, Any
from utils import GroupItemDTO


def map_to_group_item_dto(name: str, members: List[str]) -> GroupItemDTO:
    """
    Map group data to GroupItemDTO.
    
    Args:
        name: Name of the group
        members: List of member UIDs
        
    Returns:
        GroupItemDTO instance
    """
    return GroupItemDTO(
        name=name,
        members=members,
        member_count=len(members)
    )
