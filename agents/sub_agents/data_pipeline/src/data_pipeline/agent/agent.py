from smolagents.agents import CodeAgent
from utils import logger, load_config, get_config
from utils.models.ragrenn import RagrennModel
from data_pipeline.agent.tools import fetch_tool, preprocess_tool, group_tool


class DataPipelineAgent:
    """
    DataPipelineAgent
    -----------------
    Executes end-to-end data pipeline tasks using SmolAgent tools.

    Features:
        - Fetches raw data
        - Preprocesses and cleans datasets
        - Groups or analyzes preprocessed data
        - Retries failed runs with configurable attempts
    """

    def __init__(self):
        load_config()
        config = get_config().LLM_MODULES.DATA_PIPELINE

        # Initialize model
        self.model = RagrennModel(model_name= config.MODEL.NAME, base_url= config.MODEL.BASE_URL).to_smol_model()

        # Load pipeline instructions
        self.instructions = config.INSTRUCTIONS
        self.retries = config.SETTINGS.RETRIES

        # Register tools
        self.tools = [fetch_tool, preprocess_tool, group_tool]

        logger.info("DataPipelineAgent initialized with tools: %s", [t.name for t in self.tools])

    # ---------------------------------------------------------
    # Execute Task
    # ---------------------------------------------------------
    def _execute(self, task: str):
        """
        Execute the given task using SmolAgent's CodeAgent.
        Args:
            task (str): High-level pipeline instruction from Orchestrator.
        """
        logger.info(f"🚀 Executing task: {task}")

        # Create an isolated code agent for the task
        agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            instructions=self.instructions,
            add_base_tools=False
        )

        # Run the task
        result = agent.run(task)
        logger.info("Task execution completed successfully. Result: %s", result)
        return result

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

        return None


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
    task = task or "Fetch raw data, preprocess, and group students."
    result = agent.run(task)
    return result


# ----------------------------
# CLI Usage
# ----------------------------
if __name__ == "__main__":
    test_task = "Fetch attendance data, preprocess, and group students by recurring sessions."
    output = main(test_task)
    print("PipelineAgent output:", output)