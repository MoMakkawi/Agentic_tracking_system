# SPDX-FileCopyrightText: 2025-present MoMakkawi <MoMakkawi@hotmail.com>
#
# SPDX-License-Identifier: MIT

"""
Short-Term Memory Implementation.

Wraps smolagents' built-in conversation history to provide consistent
interface through the BaseMemory abstract class.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from smolagents.agents import ToolCallingAgent

from .base import BaseMemory, MemoryType, MemoryEntry
from utils import logger


class ShortTermMemory(BaseMemory):
    """
    Short-term memory for conversation history.
    
    This memory type wraps the smolagents ToolCallingAgent's internal memory,
    providing conversation continuity across multiple run() calls. It tracks
    tasks, results, and interaction steps within a session.
    
    The memory persists as long as the agent instance exists. Use clear()
    to reset conversation history without destroying the agent.
    
    Attributes:
        _agent: Reference to the ToolCallingAgent whose memory we're managing
        _conversation_log: Internal log of task/result pairs for quick access
        
    Example:
        agent = ToolCallingAgent(...)
        stm = ShortTermMemory(agent)
        
        # After agent.run() calls, check memory:
        print(stm.get_stats())  # {'entry_count': 5, 'conversation_turns': 2, ...}
    """
    
    def __init__(self, agent: ToolCallingAgent):
        """
        Initialize short-term memory.
        
        Args:
            agent: The ToolCallingAgent instance to manage memory for
        """
        super().__init__("short_term", MemoryType.SHORT_TERM)
        self._agent = agent
        self._conversation_log: List[MemoryEntry] = []
        logger.info("ShortTermMemory initialized for agent")

    def add(self, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Record a conversation turn (task + result).
        
        Note: The actual conversation steps are managed by smolagents internally.
        This method provides an additional log of high-level interactions.
        
        Args:
            key: Task description or identifier
            value: Result or response
            metadata: Optional additional context (e.g., timestamp, token count)
            
        Returns:
            True if recorded successfully
        """
        if not self.is_enabled:
            logger.debug("ShortTermMemory disabled, skipping add")
            return False
            
        entry = MemoryEntry(
            key=key,
            value=value,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self._conversation_log.append(entry)
        logger.debug(f"Recorded conversation turn: {key[:50]}...")
        return True

    def get(self, key: str) -> Optional[Any]:
        """
        Get a specific conversation entry by key (task description).
        
        Args:
            key: The task description to search for
            
        Returns:
            The result for that task, or None if not found
        """
        for entry in reversed(self._conversation_log):
            if entry.key == key:
                return entry.value
        return None

    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """
        Get the N most recent conversation turns.
        
        Args:
            n: Number of turns to retrieve
            
        Returns:
            List of recent memory entries
        """
        return self._conversation_log[-n:]

    def search(self, query: str, limit: int = 10) -> List[MemoryEntry]:
        """
        Search conversation history by keyword.
        
        Simple substring matching on task descriptions.
        
        Args:
            query: Search string
            limit: Maximum results
            
        Returns:
            Matching conversation entries
        """
        results = []
        query_lower = query.lower()
        for entry in reversed(self._conversation_log):
            if query_lower in entry.key.lower() or query_lower in str(entry.value).lower():
                results.append(entry)
                if len(results) >= limit:
                    break
        return results

    def clear(self) -> None:
        """
        Clear conversation history.
        
        This resets both our internal log and the smolagents memory.
        The agent instance remains valid for new conversations.
        """
        # Clear our internal log
        self._conversation_log.clear()
        
        # Clear smolagents' internal memory
        if hasattr(self._agent, 'memory') and self._agent.memory is not None:
            try:
                self._agent.memory.reset()
                logger.info("ShortTermMemory cleared (both internal and smolagents)")
            except Exception as e:
                logger.warning(f"Failed to reset smolagents memory: {e}")
        else:
            logger.info("ShortTermMemory internal log cleared")

    def get_all(self) -> List[MemoryEntry]:
        """
        Get all conversation entries.
        
        Returns:
            All conversation turns recorded
        """
        return list(self._conversation_log)

    def load_history(self, messages: List[Any]) -> None:
        """
        Load conversation history into memory.
        
        Args:
            messages: List of chat messages from ChatService
        """
        self._conversation_log.clear()
        
        # Format messages into conversation turns (pairs of user/assistant)
        # Note: We store them in our log. Re-injecting into smolagents is handled
        # via the first run() call context if necessary, or by appending steps.
        
        for msg in messages:
            entry = MemoryEntry(
                key=f"{msg.role.capitalize()}: {msg.content[:50]}...",
                value=msg.content,
                timestamp=msg.timestamp,
                metadata={"role": msg.role, "persisted": True}
            )
            self._conversation_log.append(entry)
            
        logger.info(f"Loaded {len(messages)} messages into ShortTermMemory log")

    def get_agent_memory_steps(self) -> List[Dict[str, Any]]:
        """
        Get the raw smolagents memory steps.
        
        Returns:
            List of memory steps from the underlying agent
        """
        if hasattr(self._agent, 'memory') and self._agent.memory is not None:
            try:
                return list(self._agent.memory.get_full_steps())
            except Exception as e:
                logger.warning(f"Failed to get agent memory steps: {e}")
                return []
        return []

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about short-term memory.
        
        Returns:
            Dictionary with memory statistics
        """
        agent_steps = self.get_agent_memory_steps()
        
        return {
            "name": self.name,
            "memory_type": self.memory_type.value,
            "enabled": self.is_enabled,
            "created_at": self.created_at.isoformat(),
            "conversation_turns": len(self._conversation_log),
            "agent_memory_steps": len(agent_steps),
            "has_agent_memory": hasattr(self._agent, 'memory') and self._agent.memory is not None,
        }

    def get_formatted_history(self) -> str:
        """
        Get conversation history as formatted string.
        
        Useful for debugging or logging the conversation flow.
        
        Returns:
            Human-readable conversation history
        """
        if not self._conversation_log:
            return "No conversation history."
        
        lines = ["=== Conversation History ==="]
        for i, entry in enumerate(self._conversation_log, 1):
            lines.append(f"\n[Turn {i}] {entry.timestamp.strftime('%H:%M:%S')}")
            lines.append(f"Task: {entry.key[:100]}...")
            lines.append(f"Result: {str(entry.value)[:200]}...")
        return "\n".join(lines)

    def get_memory_length(self) -> int:
        """
        Returns the number of steps in the underlying agent memory.
        """
        return len(self.get_agent_memory_steps())
