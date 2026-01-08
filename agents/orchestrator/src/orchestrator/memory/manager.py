# SPDX-FileCopyrightText: 2025-present MoMakkawi <MoMakkawi@hotmail.com>
#
# SPDX-License-Identifier: MIT

"""
Memory Manager.

Central registry for managing multiple memory types. Provides unified
interface for registering, accessing, and controlling all memory instances.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime

from .base import BaseMemory, MemoryType
from utils import logger


class MemoryManager:
    """
    Central manager for all memory types.
    
    The MemoryManager acts as a registry and controller for multiple memory
    instances. It provides unified access to different memory types and
    enables bulk operations across all registered memories.
    
    Attributes:
        _memories: Dictionary mapping memory names to instances
        created_at: When the manager was instantiated
        
    Example:
        manager = MemoryManager()
        
        # Register memories
        manager.register(ShortTermMemory(agent))
        manager.register(LongTermMemory(db_connection))  # Future
        
        # Access specific memory
        stm = manager.get("short_term")
        stm.add("task1", "result1")
        
        # Bulk operations
        manager.clear_all()
        stats = manager.get_all_stats()
    """
    
    def __init__(self):
        """Initialize the memory manager."""
        self._memories: Dict[str, BaseMemory] = {}
        self.created_at = datetime.now()
        logger.info("MemoryManager initialized")

    def register(self, memory: BaseMemory) -> None:
        """
        Register a memory instance.
        
        Args:
            memory: Memory instance to register
            
        Raises:
            ValueError: If a memory with the same name is already registered
        """
        if memory.name in self._memories:
            logger.warning(f"Memory '{memory.name}' already registered, replacing...")
        
        self._memories[memory.name] = memory
        logger.info(f"Registered memory: {memory.name} (type: {memory.memory_type.value})")

    def unregister(self, name: str) -> bool:
        """
        Unregister a memory by name.
        
        Args:
            name: Name of the memory to remove
            
        Returns:
            True if removed, False if not found
        """
        if name in self._memories:
            del self._memories[name]
            logger.info(f"Unregistered memory: {name}")
            return True
        return False

    def get(self, name: str) -> Optional[BaseMemory]:
        """
        Get a memory instance by name.
        
        Args:
            name: Name of the memory to retrieve
            
        Returns:
            The memory instance, or None if not found
        """
        return self._memories.get(name)

    def get_by_type(self, memory_type: MemoryType) -> List[BaseMemory]:
        """
        Get all memories of a specific type.
        
        Args:
            memory_type: The type of memories to retrieve
            
        Returns:
            List of memories matching the type
        """
        return [m for m in self._memories.values() if m.memory_type == memory_type]

    def list_memories(self) -> List[str]:
        """
        List all registered memory names.
        
        Returns:
            List of registered memory names
        """
        return list(self._memories.keys())

    def has_memory(self, name: str) -> bool:
        """
        Check if a memory is registered.
        
        Args:
            name: Name of the memory to check
            
        Returns:
            True if registered, False otherwise
        """
        return name in self._memories

    def clear(self, name: str) -> bool:
        """
        Clear a specific memory by name.
        
        Args:
            name: Name of the memory to clear
            
        Returns:
            True if cleared, False if not found
        """
        memory = self.get(name)
        if memory:
            memory.clear()
            logger.info(f"Cleared memory: {name}")
            return True
        return False

    def clear_all(self) -> None:
        """Clear all registered memories."""
        for name, memory in self._memories.items():
            try:
                memory.clear()
                logger.info(f"Cleared memory: {name}")
            except Exception as e:
                logger.error(f"Failed to clear memory '{name}': {e}")

    def enable(self, name: str) -> bool:
        """
        Enable a specific memory.
        
        Args:
            name: Name of the memory to enable
            
        Returns:
            True if enabled, False if not found
        """
        memory = self.get(name)
        if memory:
            memory.enable()
            return True
        return False

    def disable(self, name: str) -> bool:
        """
        Disable a specific memory (stops recording but preserves data).
        
        Args:
            name: Name of the memory to disable
            
        Returns:
            True if disabled, False if not found
        """
        memory = self.get(name)
        if memory:
            memory.disable()
            return True
        return False

    def enable_all(self) -> None:
        """Enable all registered memories."""
        for memory in self._memories.values():
            memory.enable()

    def disable_all(self) -> None:
        """Disable all registered memories."""
        for memory in self._memories.values():
            memory.disable()

    def get_stats(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a specific memory.
        
        Args:
            name: Name of the memory
            
        Returns:
            Memory statistics, or None if not found
        """
        memory = self.get(name)
        if memory:
            return memory.get_stats()
        return None

    def get_all_stats(self) -> Dict[str, Dict[str, Any]]:
        """
        Get statistics from all registered memories.
        
        Returns:
            Dictionary mapping memory names to their statistics
        """
        stats = {
            "_manager": {
                "registered_memories": len(self._memories),
                "memory_names": list(self._memories.keys()),
                "created_at": self.created_at.isoformat(),
            }
        }
        for name, memory in self._memories.items():
            try:
                stats[name] = memory.get_stats()
            except Exception as e:
                stats[name] = {"error": str(e)}
        return stats

    def __len__(self) -> int:
        """Return the number of registered memories."""
        return len(self._memories)

    def __repr__(self) -> str:
        memory_list = ", ".join(self._memories.keys()) if self._memories else "none"
        return f"MemoryManager(memories=[{memory_list}])"
