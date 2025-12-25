from smolagents.agents import CodeAgent
from typing import Optional
from utils import logger, load_config, get_config
from utils import RagrennModel
from .tools import clean_data_insighter_tool, groups_insighter_tool#, alerts_insighter_tool
from utils import RepositoryFactory

class KnowledgeInsightAgent:
    """
    KnowledgeInsightAgent
    -----------------------
    Analyzes knowledge using SmolAgent tools.

    Features:
        - Loads precomputed knowledge
        - Runs with retry logic
        - Uses LLM reasoning on small summaries
    """

    def __init__(self):
        load_config()
        config = get_config().LLM_MODULES.KNOWLEDGE_INSIGHT

        # Initialize model
        self.model = RagrennModel(model_config=config).to_smol_model()

        # Initialize default task
        self.default_task = config.DEFAULT_TASK

        # Initialize settings
        self.retries = config.SETTINGS.RETRIES
        self.max_steps = config.SETTINGS.MAX_STEPS
        self.verbosity_level = config.SETTINGS.VERBOSITY_LEVEL

        # Register tools
        self.tools = [clean_data_insighter_tool, groups_insighter_tool]#, alerts_insighter_tool]

    # ---------------------------------------------------------
    # Execute Task
    # ---------------------------------------------------------
    def _execute(self, task: Optional[str] = None):
        """
        Execute the given task using SmolAgent's CodeAgent.
        Args:
            task (Optional[str]): High-level instruction/question from orchestrator.
        """
        logger.info(f"Executing task: {task}")

        # Create an isolated code agent for the task
        agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            max_steps=self.max_steps,  # Limit steps: understand -> generate -> execute
            verbosity_level=self.verbosity_level
        )


        # Run the task
        task = task or self.default_task
        instructions = self._build_task_instructions(task)

        result = agent.run(instructions)
        logger.info("Task execution completed successfully. Result: %s", result)
        return result

    def _build_task_instructions(self, task: Optional[str] = None):
        """Builds the agent instructions by fetching schemas from repositories."""
        config_paths = get_config().PATHS
        
        # Initialize data schemas
        clean_data_schema = RepositoryFactory.get_repository(config_paths.PREPROCESSED).get_schema_info()
        groups_data_schema = RepositoryFactory.get_repository(config_paths.GROUPS).get_schema_info()
        timestamp_alerts_data_schema = RepositoryFactory.get_repository(config_paths.ALERTS.VALIDATION.TIMESTAMP).get_schema_info()
        identity_alerts_data_schema = RepositoryFactory.get_repository(config_paths.ALERTS.VALIDATION.IDENTITY).get_schema_info()
        device_alerts_data_schema = RepositoryFactory.get_repository(config_paths.ALERTS.VALIDATION.DEVICE).get_schema_info()
        
        # build task instructions
        instructions = get_config().LLM_MODULES.KNOWLEDGE_INSIGHT.INSTRUCTIONS.format(
            clean_data_schema=clean_data_schema,
            groups_data_schema=groups_data_schema,
            timestamp_alerts_data_schema=timestamp_alerts_data_schema,
            identity_alerts_data_schema=identity_alerts_data_schema,
            device_alerts_data_schema=device_alerts_data_schema,
            task=task)
        return instructions

    # ---------------------------------------------------------
    # Run with Retries (Used by Orchestrator)
    # ---------------------------------------------------------
    def run(self, task: str):
        """
        Run task with retry logic.
        """
        for attempt in range(1, self.retries + 1):
            try:
                return self._execute(task)
            except Exception as e:
                logger.exception(f"Attempt {attempt} failed: {e}")
                if attempt == self.retries:
                    logger.error("All attempts failed for task: %s", task)
                    raise
                logger.info("Retrying...")

# ----------------------------
# Callable main() for CLI or orchestration
# ----------------------------
def main(task: Optional[str] = None):
    """
    Entry point for KnowledgeInsightAgent.
    Args:
        task (Optional[str]): Question/instruction to the agent
    Returns:
        Any: Result of knowledge insight
    """
    agent = KnowledgeInsightAgent()
    result = agent.run(task)
    return result

