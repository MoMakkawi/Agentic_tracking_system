from smolagents.agents import ToolCallingAgent
from typing import Optional, List, Dict, Any
from utils import logger, get_config, load_config
from utils import RagrennModel
from .tools import pipeline_agent_tool, validation_agent_tool, group_identifier_agent_tool, insighter_agent_tool 
from .memory import MemoryManager, ShortTermMemory, BaseMemory


class Orchestrator:
    """
    Orchestrator Agent with Extensible Memory Management.
    
    Coordinates multiple sub-agents (pipeline, validation, group identification, 
    knowledge insight) using SmolAgent tools. Features a modular memory system
    that supports multiple memory types.
    
    Memory Types:
        - short_term: Conversation history within a session (enabled by default)
        - long_term: Persistent memory across sessions (future)
        - semantic: Knowledge/facts memory (future)
        - episodic: Event/experience memory (future)
    
    Features:
        - Executes complete pipeline, validation, identification, and knowledge insight workflows
        - Delegates tasks to specialized sub-agents
        - Supports configurable instructions and retry logic
        - Extensible memory system for multiple memory types
    
    Example:
        orchestrator = Orchestrator.get_instance()
        
        # Run tasks (memory persists between calls)
        result1 = orchestrator.run("Who is the most late student?")
        result2 = orchestrator.run("What group is that student in?")  # References context
        
        # Access memory system
        stm = orchestrator.get_memory("short_term")
        print(stm.get_stats())
        
        # Clear specific memory
        orchestrator.memory_manager.clear("short_term")
    """

    # Singleton instance
    _instance: 'Orchestrator' = None

    def __init__(self):
        """Initialize the Orchestrator with agent and memory system."""
        load_config()
        config = get_config().LLM_MODULES.ORCHESTRATOR

        # Initialize model
        self.model = RagrennModel(model_config=config).to_smol_model()

        # Load orchestrator instructions
        self.instructions = config.INSTRUCTIONS
        self.retries = config.SETTINGS.RETRIES

        # Initialize default task
        self.default_task = config.DEFAULT_TASK

        # Register tools
        self.tools = [pipeline_agent_tool, validation_agent_tool, group_identifier_agent_tool, insighter_agent_tool]

        # Initialize the agent (single instance for memory persistence)
        self._agent = ToolCallingAgent(
            tools=self.tools,
            model=self.model,
            instructions=self.instructions,
            add_base_tools=False
        )

        # ==============================================
        # Initialize Memory System
        # ==============================================
        self.memory_manager = MemoryManager()
        
        # Register default memory types
        self._short_term_memory = ShortTermMemory(self._agent)
        self.memory_manager.register(self._short_term_memory)
        
        # Future memory types will be registered here:
        # self.memory_manager.register(LongTermMemory(...))
        # self.memory_manager.register(SemanticMemory(...))
        # ==============================================

        logger.info("OrchestratorAgent initialized with tools: %s", [t.name for t in self.tools])
        logger.info("Memory system initialized: %s", self.memory_manager.list_memories())

    # ---------------------------------------------------------
    # Task Execution
    # ---------------------------------------------------------
    def _execute(self, task: str, reset_memory: bool = False) -> str:
        """
        Execute a task using the persistent agent.
        
        Args:
            task: The task to execute
            reset_memory: If True, clears conversation history before running
        
        Returns:
            The result of task execution
        """
        logger.info(f"Executing orchestrator task: {task}")
        
        # Get memory stats before execution
        stm = self.get_memory("short_term")
        if stm:
            logger.info(f"Memory reset: {reset_memory}, Current stats: {stm.get_stats()}")

        # Execute with smolagents (reset=False preserves history)
        result = self._agent.run(task, reset=reset_memory)
        
        # Record this interaction in our memory system
        if stm and not reset_memory:
            stm.add(key=task, value=result, metadata={"attempt": 1})
        
        logger.info("Orchestrator task completed successfully")
        if stm:
            logger.info(f"Memory stats after execution: {stm.get_stats()}")
        
        return result

    def run(self, task: Optional[str] = None, reset_memory: bool = False) -> str:
        """
        Run task with retry logic.
        
        Args:
            task: The task to execute (uses default_task if None)
            reset_memory: If True, clears conversation history before running
        
        Returns:
            The result of task execution
        """
        task = task or self.default_task
        logger.info(f"Running orchestrator task: {task}")

        for attempt in range(1, self.retries + 1):
            try:
                return self._execute(task, reset_memory=reset_memory)
            except Exception as e:
                logger.exception(f"Attempt {attempt} failed: {e}")
                if attempt == self.retries:
                    logger.error("All attempts failed for task: %s", task)
                    raise
                logger.info("Retrying orchestrator task...")

    # ---------------------------------------------------------
    # Memory System Access
    # ---------------------------------------------------------
    def get_memory(self, name: str) -> Optional[BaseMemory]:
        """
        Get a specific memory by name.
        
        Args:
            name: Memory name (e.g., 'short_term', 'long_term')
        
        Returns:
            The memory instance, or None if not found
        """
        return self.memory_manager.get(name)

    def clear_memory(self, name: str = "short_term") -> bool:
        """
        Clear a specific memory.
        
        Args:
            name: Memory name to clear (default: 'short_term')
        
        Returns:
            True if cleared, False if memory not found
        """
        return self.memory_manager.clear(name)

    def clear_all_memory(self) -> None:
        """Clear all registered memories."""
        self.memory_manager.clear_all()

    def get_memory_stats(self) -> Dict[str, Any]:
        """
        Get statistics from all memories.
        
        Returns:
            Dictionary with stats from all registered memories
        """
        return self.memory_manager.get_all_stats()

    # ---------------------------------------------------------
    # Backward Compatibility Methods
    # ---------------------------------------------------------
    def get_memory_length(self) -> int:
        """
        [DEPRECATED] Use get_memory('short_term').get_stats() instead.
        Returns the number of steps in short-term memory.
        """
        stm = self.get_memory("short_term")
        if stm:
            stats = stm.get_stats()
            return stats.get("agent_memory_steps", 0)
        return 0

    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        [DEPRECATED] Use get_memory('short_term').get_all() instead.
        Returns the conversation history.
        """
        stm = self.get_memory("short_term")
        if stm and isinstance(stm, ShortTermMemory):
            return [entry.to_dict() for entry in stm.get_all()]
        return []

    def get_logs(self) -> List[Dict[str, Any]]:
        """Get the agent's run logs."""
        if hasattr(self._agent, 'logs'):
            return self._agent.logs
        return []

    # ---------------------------------------------------------
    # Singleton Pattern
    # ---------------------------------------------------------
    @classmethod
    def get_instance(cls) -> 'Orchestrator':
        """
        Get the singleton Orchestrator instance.
        
        This ensures memory persists across API calls. Use this method
        instead of creating new Orchestrator() instances directly.
        
        Returns:
            The singleton Orchestrator instance
        """
        if cls._instance is None:
            logger.info("Creating new Orchestrator singleton instance...")
            cls._instance = cls()
        else:
            memory_count = len(cls._instance.memory_manager) if cls._instance.memory_manager else 0
            logger.info(f"Reusing Orchestrator instance (memories: {memory_count})")
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """
        Destroy the current singleton instance.
        
        Forces a fresh start on next get_instance() call.
        Use this to completely reset the orchestrator (new model, new tools, new memory).
        """
        if cls._instance is not None:
            logger.info("Resetting Orchestrator singleton instance...")
            cls._instance = None


# ----------------------------
# Main Entry Point
# ----------------------------
def main(task: str = None, reset_memory: bool = False) -> str:
    """
    Entry point for the Orchestrator.
    
    Uses singleton pattern to maintain memory across calls.
    
    Args:
        task: The task to execute (uses default if None)
        reset_memory: If True, clears conversation history before running
    
    Returns:
        The result of task execution
    """
    orchestrator = Orchestrator.get_instance()
    return orchestrator.run(task, reset_memory=reset_memory)
