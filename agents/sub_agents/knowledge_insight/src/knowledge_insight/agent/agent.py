from smolagents.agents import CodeAgent
from typing import Optional
from utils import logger, load_config, get_config
from utils import RagrennModel
from utils import CsvRepository, JsonRepository
from .tools import data_insighter_tool, groups_insighter_tool, alerts_insighter_tool

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
        self.instructions = config.INSTRUCTIONS

        # Initialize settings
        self.retries = config.SETTINGS.RETRIES
        self.max_steps = config.SETTINGS.MAX_STEPS
        self.verbosity_level = config.SETTINGS.VERBOSITY_LEVEL

        # Register tools
        self.tools = [data_insighter_tool, groups_insighter_tool, alerts_insighter_tool]

    # ---------------------------------------------------------
    # Execute Task
    # ---------------------------------------------------------
    def _execute(self, task: str):
        """
        Execute the given task using SmolAgent's CodeAgent.
        Args:
            task (str): High-level instruction/question from orchestrator.
        """
        # Create an isolated code agent for the task
        agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            max_steps=self.max_steps,
            verbosity_level=self.verbosity_level,
            instructions=self.instructions
        )


        # Run the task
        enriched_task = self._enrich_task(task)

        result = agent.run(enriched_task)
        return result

    def _enrich_task(self, task: str):
        """Builds the user task by fetching schemas from repositories."""
        config_paths = get_config().PATHS
        
        # Initialize data schemas
        clean_data_schema = JsonRepository(config_paths.PREPROCESSED).get_schema_info()
        groups_data_schema = JsonRepository(config_paths.GROUPS).get_schema_info()
        identity_alerts_schema = CsvRepository(config_paths.ALERTS.VALIDATION.IDENTITY).get_schema_info()
        timestamp_alerts_schema = CsvRepository(config_paths.ALERTS.VALIDATION.TIMESTAMP).get_schema_info()
        device_alerts_schema = CsvRepository(config_paths.ALERTS.VALIDATION.DEVICE).get_schema_info()
        
        # build task enriched
        enriched_task = get_config().LLM_MODULES.KNOWLEDGE_INSIGHT.IMPROVED_TASK.format(
            clean_data_schema=clean_data_schema,
            groups_data_schema=groups_data_schema,
            timestamp_alerts_schema=timestamp_alerts_schema,
            identity_alerts_schema=identity_alerts_schema,
            device_alerts_schema=device_alerts_schema,
            task=task)
        return enriched_task

    # ---------------------------------------------------------
    # Run with Retries (Used by Orchestrator)
    # ---------------------------------------------------------
    def run(self, task: Optional[str] = None):
        """
        Run task with retry logic.
        """

        task = task or self.default_task
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