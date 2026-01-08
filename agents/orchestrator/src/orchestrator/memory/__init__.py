# SPDX-FileCopyrightText: 2025-present MoMakkawi <MoMakkawi@hotmail.com>
#
# SPDX-License-Identifier: MIT

"""
Extensible Memory System for Orchestrator Agent.

This module provides a modular memory architecture that supports multiple
memory types (short-term, long-term, semantic, etc.) with easy extensibility.

Example usage:
    from .memory import MemoryManager, ShortTermMemory
    
    manager = MemoryManager()
    manager.register(ShortTermMemory(agent=my_agent))
    
    # Access specific memory
    stm = manager.get("short_term")
    stm.get_stats()
"""

from .base import BaseMemory, MemoryType
from .short_term import ShortTermMemory
from .manager import MemoryManager

__all__ = [
    "BaseMemory",
    "MemoryType",
    "ShortTermMemory",
    "MemoryManager",
]
