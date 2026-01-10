# SPDX-FileCopyrightText: 2025-present MoMakkawi <MoMakkawi@hotmail.com>
#
# SPDX-License-Identifier: MIT

"""
Base Memory Abstract Class.

Defines the interface that all memory types must implement.
This enables polymorphic handling of different memory types
(short-term, long-term, semantic, episodic, etc.).
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


class MemoryType(Enum):
    """Enumeration of available memory types."""
    SHORT_TERM = "short_term"       # Conversation history within a session
    LONG_TERM = "long_term"         # Persistent memory across sessions
    SEMANTIC = "semantic"           # Knowledge/facts memory
    EPISODIC = "episodic"           # Event/experience memory
    WORKING = "working"             # Active processing memory
    PROCEDURAL = "procedural"       # Skills/how-to memory


@dataclass
class MemoryEntry:
    """
    Standard structure for a memory entry.
    
    Attributes:
        key: Unique identifier for the entry
        value: The actual content/data
        timestamp: When the entry was created
        metadata: Optional additional information
    """
    key: str
    value: Any
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary representation."""
        return {
            "key": self.key,
            "value": self.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


class BaseMemory(ABC):
    """
    Abstract base class for all memory types.
    
    All memory implementations must inherit from this class and implement
    the required abstract methods. This ensures consistent interface across
    different memory types and enables the MemoryManager to handle them
    polymorphically.
    
    Attributes:
        name: Human-readable name for this memory instance
        memory_type: The type of memory (from MemoryType enum)
        created_at: Timestamp when this memory was instantiated
        
    Example implementation:
        class LongTermMemory(BaseMemory):
            def __init__(self):
                super().__init__("long_term", MemoryType.LONG_TERM)
                self._storage = {}  # Or database connection
            
            def add(self, key, value, metadata=None):
                # Store to persistent storage
                ...
    """
    
    def __init__(self, name: str, memory_type: MemoryType):
        """
        Initialize the base memory.
        
        Args:
            name: Identifier for this memory instance
            memory_type: The type of memory from MemoryType enum
        """
        self.name = name
        self.memory_type = memory_type
        self.created_at = datetime.now()
        self._enabled = True

    @property
    def is_enabled(self) -> bool:
        """Check if this memory is currently enabled."""
        return self._enabled

    def enable(self) -> None:
        """Enable this memory."""
        self._enabled = True

    def disable(self) -> None:
        """Disable this memory (stops recording but preserves data)."""
        self._enabled = False

    @abstractmethod
    def add(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Store a memory entry.
        
        Args:
            key: Unique identifier for the entry
            value: The content to store
            metadata: Optional additional information
            
        Returns:
            True if successfully stored, False otherwise
        """
        pass

    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a memory entry by key.
        
        Args:
            key: The identifier of the entry to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        pass

    @abstractmethod
    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """
        Get the N most recent memory entries.
        
        Args:
            n: Number of entries to retrieve
            
        Returns:
            List of recent memory entries
        """
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """
        Search memories by query (implementation varies by memory type).
        
        Args:
            query: Search query string
            limit: Maximum results to return
            
        Returns:
            List of matching memory entries
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all memory entries."""
        pass

    @abstractmethod
    def get_all(self) -> List[MemoryEntry]:
        """
        Get all memory entries.
        
        Returns:
            List of all memory entries
        """
        pass

    @abstractmethod
    def get_memory_length(self) -> int:
        """
        Get the size/length of the memory.
        
        Returns:
            Integer representing memory size
        """
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about this memory.
        
        Returns:
            Dictionary containing memory statistics such as:
            - entry_count: Number of entries
            - memory_type: Type of memory
            - enabled: Whether memory is active
            - created_at: When memory was created
            - additional type-specific stats
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', type={self.memory_type.value}, enabled={self._enabled})"
