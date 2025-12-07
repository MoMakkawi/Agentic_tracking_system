from smolagents.agents import CodeAgent
from typing import Optional
from utils import logger, load_config, get_config
from utils import RagrennModel
from .tools import attendance_mapper_tool, save_tool


class GroupIdentifierAgent:
    """
    GroupIdentifierAgent
    -----------------------
    Identifies student groups from attendance data using SmolAgent tools.

    Features:
        - Loads precomputed attendance groups
        - Answers questions like "Find IoT MSc group"
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
        self.tools = [attendance_mapper_tool, save_tool]

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
            instructions=self.instructions,
            add_base_tools=False
        )

        # Run the task
        task = task or self.default_task
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
