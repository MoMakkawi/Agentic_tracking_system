from smolagents.agents import CodeAgent
from utils import RagrennModel, logger, load_config, get_config
from .tools import fetch_tool, preprocess_tool

class DataPipelineAgent:
    """
    DataPipelineAgent
    -----------------
    Executes end-to-end data pipeline tasks using SmolAgent tools.

    Features:
        - Fetches ics + logs data
        - Preprocesses and cleans datasets
        - Retries failed runs with configurable attempts
    """

    def __init__(self):
        load_config()
        config = get_config().LLM_MODULES.DATA_PIPELINE

        # Initialize model
        self.model = RagrennModel(model_config=config).to_smol_model()

        # Load pipeline instructions
        self.default_task = config.DEFAULT_TASK
        self.instructions = config.INSTRUCTIONS
        self.retries = config.SETTINGS.RETRIES

        # Register tools
        self.tools = [fetch_tool, preprocess_tool]

    # ---------------------------------------------------------
    # Execute Task
    # ---------------------------------------------------------
    def _execute(self, task: str):
        """
        Execute the given task using SmolAgent's CodeAgent.
        Args:
            task (str): High-level pipeline instruction from Orchestrator.
        """
        
        # Create an isolated code agent for the task
        agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            instructions=self.instructions,
            add_base_tools=False
        )

        # Run the task
        result = agent.run(task)
        return result

    # ---------------------------------------------------------
    # Run with Retries (Used by Orchestrator)
    # ---------------------------------------------------------
    def run(self, task: str):
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
# Callable main() for ToolCallAgent
# ----------------------------
def main(task: str = None):
    """
    Entry point for ToolCallAgent.
    Args:
        task (str): Task description. If None, uses default task.
    Returns:
        Any: Result of pipeline execution.
    """
    agent = DataPipelineAgent()
    result = agent.run(task)
    return result