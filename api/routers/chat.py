"""
Chat router for conversation management API endpoints.

This module provides REST endpoints for creating, reading, updating,
and deleting chat conversations.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional

from api.models.chat import (
    ChatConversation,
    ChatCreateRequest,
    ChatMessageRequest,
    ChatUpdateTitleRequest,
    ChatListResponse,
    ChatStatsResponse
)
from api.services.chat_service import ChatService
from utils import logger

router = APIRouter()


def get_chat_service() -> ChatService:
    """Dependency injection for ChatService."""
    return ChatService()


@router.post("/", response_model=ChatConversation)
async def create_conversation(
    request: ChatCreateRequest = None,
    service: ChatService = Depends(get_chat_service)
):
    """
    Create a new chat conversation.
    
    Returns the newly created conversation with a unique ID.
    """
    logger.info("Creating new conversation")
    title = request.title if request else None
    return service.create_conversation(title)


@router.get("/", response_model=ChatListResponse)
async def list_conversations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    service: ChatService = Depends(get_chat_service)
):
    """
    List all conversations with pagination.
    
    Returns conversations sorted by most recently updated.
    """
    logger.info(f"Listing conversations (page={page}, limit={limit})")
    return service.list_conversations(page=page, limit=limit)


@router.get("/stats", response_model=ChatStatsResponse)
async def get_chat_stats(
    service: ChatService = Depends(get_chat_service)
):
    """
    Get chat statistics for the dashboard.
    
    Returns total conversations, messages, and activity metrics.
    """
    logger.info("Getting chat statistics")
    return service.get_stats()


@router.get("/{conversation_id}", response_model=ChatConversation)
async def get_conversation(
    conversation_id: str,
    service: ChatService = Depends(get_chat_service)
):
    """
    Get a specific conversation by ID.
    
    Returns the full conversation including all messages.
    """
    logger.info(f"Getting conversation: {conversation_id}")
    conversation = service.get_conversation(conversation_id)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.post("/{conversation_id}/message", response_model=ChatConversation)
async def add_message(
    conversation_id: str,
    request: ChatMessageRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Add a message to a conversation.
    
    Returns the updated conversation with the new message.
    """
    logger.info(f"Adding {request.role} message to conversation {conversation_id}")
    
    conversation = service.add_message(
        conversation_id=conversation_id,
        role=request.role,
        content=request.content,
        status=request.status
    )
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    service: ChatService = Depends(get_chat_service)
):
    """
    Delete a conversation.
    
    Returns success status.
    """
    logger.info(f"Deleting conversation: {conversation_id}")
    
    success = service.delete_conversation(conversation_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return {"status": "deleted", "conversation_id": conversation_id}


@router.patch("/{conversation_id}/title", response_model=ChatConversation)
async def update_conversation_title(
    conversation_id: str,
    request: ChatUpdateTitleRequest,
    service: ChatService = Depends(get_chat_service)
):
    """
    Update a conversation title.
    
    Returns the updated conversation with the new title.
    """
    logger.info(f"Updating title for conversation {conversation_id} to: {request.title}")
    
    conversation = service.update_title(conversation_id, request.title)
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    return conversation
