# SPDX-FileCopyrightText: 2025-present MoMakkawi <MoMakkawi@hotmail.com>
#
# SPDX-License-Identifier: MIT

"""
Orchestrator Agent Package.

Provides the main Orchestrator agent with extensible memory management
for coordinating sub-agents in the attendance analytics system.
"""

from .src.orchestrator.agent import main as orchestrator_run
from .src.orchestrator.agent import Orchestrator
from .src.orchestrator.memory import (
    BaseMemory,
    MemoryType,
    ShortTermMemory,
    MemoryManager,
)


# ---------------------------------------------------------
# Convenience Functions
# ---------------------------------------------------------
def get_orchestrator_instance() -> Orchestrator:
    """
    Get the singleton Orchestrator instance with preserved memory.
    
    Returns:
        The singleton Orchestrator instance
    """
    return Orchestrator.get_instance()


def clear_orchestrator_memory(name: str = "short_term") -> bool:
    """
    Clear a specific memory while keeping the instance.
    
    Args:
        name: Memory name to clear (default: 'short_term')
    
    Returns:
        True if cleared, False if memory not found
    """
    instance = Orchestrator.get_instance()
    return instance.clear_memory(name)


def reset_orchestrator() -> None:
    """Completely reset the orchestrator (new instance, no memory)."""
    Orchestrator.reset_instance()


def get_memory_stats() -> dict:
    """
    Get current memory statistics from all registered memories.
    
    Returns:
        Dictionary with stats from all memories
    """
    instance = Orchestrator.get_instance()
    return instance.get_memory_stats()


def get_memory(name: str = "short_term"):
    """
    Get a specific memory by name.
    
    Args:
        name: Memory name (e.g., 'short_term', 'long_term')
    
    Returns:
        The memory instance, or None if not found
    """
    instance = Orchestrator.get_instance()
    return instance.get_memory(name)


__all__ = [
    # Main exports
    "orchestrator_run",
    "Orchestrator",
    
    # Memory classes
    "BaseMemory",
    "MemoryType", 
    "ShortTermMemory",
    "MemoryManager",
    
    # Convenience functions
    "get_orchestrator_instance",
    "clear_orchestrator_memory",
    "reset_orchestrator",
    "get_memory_stats",
    "get_memory",
]