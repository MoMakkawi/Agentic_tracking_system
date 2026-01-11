from smolagents.agents import CodeAgent
from typing import Optional
from utils import logger, load_config, get_config
from utils import RagrennModel, JsonRepository, CsvRepository
from .tools import louvain_clustering_tool, save_tool

class GroupIdentifierAgent:
    """
    GroupIdentifierAgent
    -----------------------
    Identifies student groups from attendance data using SmolAgent tools.

    Features:
        - Loads precomputed attendance groups
        - Runs with retry logic
        - Uses LLM reasoning on small summaries
    """

    def __init__(self):
        load_config()
        config = get_config().LLM_MODULES.GROUP_IDENTIFIER

        # Initialize model
        self.model = RagrennModel(model_config=config).to_smol_model()

        # Load instructions, default task & retries
        self.instructions = config.INSTRUCTIONS
        self.default_task = config.DEFAULT_TASK
        self.retries = config.SETTINGS.RETRIES

        # Register tools
        self.tools = [louvain_clustering_tool, save_tool]

    
    def _build_task_instructions(self, task: str):
        """Builds the agent instructions by fetching schemas from repositories."""
        config_paths = get_config().PATHS
        
        # Initialize data schemas
        clean_data_schema = JsonRepository(config_paths.PREPROCESSED).get_schema_info()
        identity_alerts_schema = CsvRepository(config_paths.ALERTS.VALIDATION.IDENTITY).get_schema_info()
          
        # build task instructions
        instructions = get_config().LLM_MODULES.GROUP_IDENTIFIER.INSTRUCTIONS.format(
            clean_data_schema=clean_data_schema,
            identity_alerts_schema=identity_alerts_schema,
            task=task)
        return instructions

    # ---------------------------------------------------------
    # Execute Task
    # ---------------------------------------------------------
    def _execute(self, task: str):
        """
        Execute the given task using SmolAgent's CodeAgent.
        Args:
            task (Optional[str]): High-level instruction/question from orchestrator.
        """

        # Create an isolated code agent for the task
        agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            add_base_tools=False
        )

        # Run the task
        task = task or self.default_task
        task_instructions=self._build_task_instructions(task)
        result = agent.run(task_instructions)
        return result

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
    Entry point for GroupIdentifierAgent.
    Args:
        task (Optional[str]): Question/instruction to the agent
    Returns:
        Any: Result of group identification
    """
    agent = GroupIdentifierAgent()
    result = agent.run(task)
    return result

# ----------------------------
# CLI Usage
# ----------------------------
if __name__ == "__main__":
    test_task = "Find the IoT MSc group who attend Coaching professionnel."
    output = main(test_task)
    print("GroupIdentifierAgent output:", output)
