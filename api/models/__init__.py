"""
Models package for API data structures.

This package contains Pydantic models for request/response validation.
"""

from .session_filters import SessionFilters, PaginationParams, SortParams
from .alert_filters import (
    PaginatedAlertResponse,
    DeviceAlertFilters,
    IdentityAlertFilters,
    TimestampAlertFilters
)
from .group_filters import GroupFilters, PaginatedGroupResponse
from .agent import AgentRequest, AgentResponse
from .chat import (
    ChatMessage,
    ChatConversation,
    ChatCreateRequest,
    ChatMessageRequest,
    ChatListResponse,
    ChatStatsResponse
)

__all__ = [
    "SessionFilters",
    "PaginationParams",
    "SortParams",
    "PaginatedAlertResponse",
    "DeviceAlertFilters",
    "IdentityAlertFilters",
    "TimestampAlertFilters",
    "GroupFilters",
    "PaginatedGroupResponse",
    "AgentRequest",
    "AgentResponse",
    "ChatMessage",
    "ChatConversation",
    "ChatCreateRequest",
    "ChatMessageRequest",
    "ChatListResponse",
    "ChatStatsResponse"
]

