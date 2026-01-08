"""
Chat models for API data structures.

This module contains Pydantic models for chat conversation persistence.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class ChatMessage(BaseModel):
    """Single message in a conversation."""
    role: Literal["user", "assistant"] = Field(..., description="Message sender role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")
    status: Optional[str] = Field(None, description="Optional status (e.g., 'success', 'error')")


class ChatConversation(BaseModel):
    """Full conversation with metadata."""
    id: str = Field(..., description="Unique conversation identifier")
    title: str = Field("New Conversation", description="Conversation title")
    messages: List[ChatMessage] = Field(default_factory=list, description="List of messages")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")


class ChatCreateRequest(BaseModel):
    """Request to create a new conversation."""
    title: Optional[str] = Field("New Conversation", description="Optional conversation title")


class ChatMessageRequest(BaseModel):
    """Request to add a message to a conversation."""
    role: Literal["user", "assistant"] = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    status: Optional[str] = Field(None, description="Optional status")


class ChatUpdateTitleRequest(BaseModel):
    """Request to update a conversation title."""
    title: str = Field(..., description="The new conversation title")


class ChatListResponse(BaseModel):
    """Response for listing conversations."""
    conversations: List[ChatConversation] = Field(..., description="List of conversations")
    total: int = Field(..., description="Total number of conversations")


class ChatStatsResponse(BaseModel):
    """Statistics about chat conversations."""
    total_conversations: int = Field(..., description="Total number of conversations")
    total_messages: int = Field(..., description="Total messages across all conversations")
    recent_conversations: int = Field(..., description="Conversations in last 7 days")
    avg_messages_per_conversation: float = Field(..., description="Average messages per conversation")
