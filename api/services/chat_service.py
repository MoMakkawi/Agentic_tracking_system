"""
Chat service for managing conversation persistence.

This module handles saving, loading, and managing chat conversations
using JSON file storage in the data/chats directory.
"""

import json
import os
import uuid
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

from api.models.chat import (
    ChatMessage,
    ChatConversation,
    ChatListResponse,
    ChatStatsResponse
)
from utils import logger


class ChatService:
    """
    Service class for chat conversation persistence.
    
    Stores conversations as JSON files in the data/chats directory.
    """
    
    def __init__(self):
        """Initialize the ChatService with storage directory."""
        self.base_path = Path(__file__).parent.parent.parent / "data" / "chats"
        self._ensure_storage_exists()
    
    def _ensure_storage_exists(self) -> None:
        """Create the storage directory if it doesn't exist."""
        self.base_path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Chat storage directory ready at: {self.base_path}")
    
    def _get_conversation_path(self, conversation_id: str) -> Path:
        """Get the file path for a conversation."""
        return self.base_path / f"{conversation_id}.json"
    
    def _serialize_conversation(self, conversation: ChatConversation) -> dict:
        """Serialize a conversation to JSON-compatible dict."""
        return {
            "id": conversation.id,
            "title": conversation.title,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat(),
                    "status": msg.status
                }
                for msg in conversation.messages
            ],
            "created_at": conversation.created_at.isoformat(),
            "updated_at": conversation.updated_at.isoformat()
        }
    
    def _deserialize_conversation(self, data: dict) -> ChatConversation:
        """Deserialize a dict to a ChatConversation."""
        return ChatConversation(
            id=data["id"],
            title=data["title"],
            messages=[
                ChatMessage(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=datetime.fromisoformat(msg["timestamp"]),
                    status=msg.get("status")
                )
                for msg in data["messages"]
            ],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"])
        )
    
    def create_conversation(self, title: Optional[str] = None) -> ChatConversation:
        """
        Create a new conversation.
        
        Args:
            title: Optional conversation title
            
        Returns:
            The newly created conversation
        """
        conversation_id = str(uuid.uuid4())
        now = datetime.now()
        
        conversation = ChatConversation(
            id=conversation_id,
            title=title or "New Conversation",
            messages=[],
            created_at=now,
            updated_at=now
        )
        
        # Save to file
        self._save_conversation(conversation)
        logger.info(f"Created new conversation: {conversation_id}")
        
        return conversation
    
    def _save_conversation(self, conversation: ChatConversation) -> None:
        """Save a conversation to file."""
        file_path = self._get_conversation_path(conversation.id)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self._serialize_conversation(conversation), f, indent=2)
    
    def get_conversation(self, conversation_id: str) -> Optional[ChatConversation]:
        """
        Get a conversation by ID.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            The conversation or None if not found
        """
        file_path = self._get_conversation_path(conversation_id)
        
        if not file_path.exists():
            logger.warning(f"Conversation not found: {conversation_id}")
            return None
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return self._deserialize_conversation(data)
        except Exception as e:
            logger.error(f"Error loading conversation {conversation_id}: {e}")
            return None
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        status: Optional[str] = None
    ) -> Optional[ChatConversation]:
        """
        Add a message to a conversation.
        
        Args:
            conversation_id: The conversation ID
            role: Message role ('user' or 'assistant')
            content: Message content
            status: Optional status
            
        Returns:
            Updated conversation or None if not found
        """
        conversation = self.get_conversation(conversation_id)
        
        if not conversation:
            return None
        
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.now(),
            status=status
        )
        
        conversation.messages.append(message)
        conversation.updated_at = datetime.now()
        
        # Auto-generate title from first user message if still default
        if conversation.title == "New Conversation" and role == "user":
            conversation.title = content[:50] + ("..." if len(content) > 50 else "")
        
        self._save_conversation(conversation)
        logger.debug(f"Added {role} message to conversation {conversation_id}")
        
        return conversation
    
    def list_conversations(
        self,
        page: int = 1,
        limit: int = 20
    ) -> ChatListResponse:
        """
        List all conversations with pagination.
        
        Args:
            page: Page number (1-indexed)
            limit: Items per page
            
        Returns:
            ChatListResponse with conversations and total count
        """
        conversations = []
        
        # Load all conversations
        for file_path in self.base_path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                conversations.append(self._deserialize_conversation(data))
            except Exception as e:
                logger.warning(f"Error loading {file_path}: {e}")
        
        # Sort by updated_at descending (most recent first)
        conversations.sort(key=lambda c: c.updated_at, reverse=True)
        
        total = len(conversations)
        
        # Apply pagination
        start = (page - 1) * limit
        end = start + limit
        paginated = conversations[start:end]
        
        return ChatListResponse(conversations=paginated, total=total)
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation.
        
        Args:
            conversation_id: The conversation ID
            
        Returns:
            True if deleted, False if not found
        """
        file_path = self._get_conversation_path(conversation_id)
        
        if not file_path.exists():
            return False
        
        try:
            os.remove(file_path)
            logger.info(f"Deleted conversation: {conversation_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation {conversation_id}: {e}")
            return False
    
    def get_stats(self) -> ChatStatsResponse:
        """
        Get chat statistics for dashboard.
        
        Returns:
            ChatStatsResponse with statistics
        """
        conversations = []
        total_messages = 0
        recent_count = 0
        seven_days_ago = datetime.now() - timedelta(days=7)
        
        for file_path in self.base_path.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                conv = self._deserialize_conversation(data)
                conversations.append(conv)
                total_messages += len(conv.messages)
                
                if conv.created_at >= seven_days_ago:
                    recent_count += 1
            except Exception as e:
                logger.warning(f"Error loading {file_path} for stats: {e}")
        
        total_conversations = len(conversations)
        avg_messages = total_messages / total_conversations if total_conversations > 0 else 0
        
        return ChatStatsResponse(
            total_conversations=total_conversations,
            total_messages=total_messages,
            recent_conversations=recent_count,
            avg_messages_per_conversation=round(avg_messages, 2)
        )
