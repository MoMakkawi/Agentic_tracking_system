from smolagents.agents import CodeAgent
from utils import logger, load_config, get_config
from utils import RagrennModel
from data_validation.agent.tools import device_validation_tool, timestamp_validation_tool, identity_validation_tool


class DataValidationAgent:
    """
    DataValidationAgent
    -------------------
    Executes end-to-end data validation tasks using SmolAgent tools.

    Features:
        - Checks device, timestamp, and identity anomalies
        - Summarizes detected issues
        - Retries failed runs with configurable attempts
    """

    def __init__(self):
        load_config()

        config = get_config().LLM_MODULES.DATA_VALIDATION

        self.model = RagrennModel(model_config=config).to_smol_model()

        # Load validation instructions
        self.instructions = config.INSTRUCTIONS
        self.retries = config.SETTINGS.RETRIES

        # Register tools
        self.tools = [device_validation_tool, timestamp_validation_tool, identity_validation_tool]

        logger.info("DataValidationAgent initialized with tools: %s", [t.name for t in self.tools])

    # ---------------------------------------------------------
    # Execute Task
    # ---------------------------------------------------------
    def _execute(self, task: str):
        """
        Execute the given validation task using SmolAgent's CodeAgent.
        Args:
            task (str): High-level validation instruction from Orchestrator.
        """
        logger.info(f"Executing validation task: {task}")

        # Create an isolated code agent for the task
        agent = CodeAgent(
            tools=self.tools,
            model=self.model,
            instructions=self.instructions,
            add_base_tools=False
        )

        # Run the task
        result = agent.run(task)
        logger.info("Validation task completed successfully. Result: %s", result)
        return result

    # ---------------------------------------------------------
    # Run with Retries (Used by Orchestrator)
    # ---------------------------------------------------------
    def run(self, task: str):
        """
        Run validation task with retry logic.
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
# Callable main() for CLI or ToolCallAgent
# ----------------------------
def main(task: str = None):
    """
    Entry point for DataValidationAgent.
    Args:
        task (str): Task description. If None, uses default task.
    Returns:
        Any: Result of validation execution.
    """
    agent = DataValidationAgent()
    task = task or (
        "Run all validation tools to check device, timestamp, and identity anomalies "
        "in the preprocessed session dataset, then summarize detected issues."
    )
    result = agent.run(task)
    return result


# ----------------------------
# CLI Usage
# ----------------------------
if __name__ == "__main__":
    output = main()
    print("DataValidationAgent output:", output)
