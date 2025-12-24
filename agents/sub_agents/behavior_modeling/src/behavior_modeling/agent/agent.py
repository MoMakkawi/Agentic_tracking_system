from smolagents.agents import ToolCallingAgent
from typing import Optional
from utils import RagrennModel, logger, load_config, get_config
from .tools import execute_python_analysis_tool
from ..core.helper import Helper

class BehaviorAnalyzerAgent:
    """
    BehaviorAnalyzerAgent
    -----------------------
    Analyzes attendance behavior by generating Python code strings
    and delegating execution to tools.
    """

    def __init__(self):
        load_config()

        # Initialize model
        config = get_config().LLM_MODULES.BEHAVIOR_MODELING
        self.model = RagrennModel(model_config=config).to_smol_model()

        # Load settings
        self.default_task = config.DEFAULT_TASK
        self.instructions = config.INSTRUCTIONS
        self.retries = config.SETTINGS.RETRIES
        self.max_steps = config.SETTINGS.MAX_STEPS

        # Register tools - use ToolCallingAgent instead of CodeAgent
        self.tools = [execute_python_analysis_tool]

        # Schema info for better code generation
        self.schema_info = Helper().get_schema_info()

    def _execute(self, task: Optional[str] = None) -> str:
        """Execute task using ToolCallingAgent."""
        task = task or self.default_task
        logger.info(f"Executing task: {task}")

        # Use ToolCallingAgent - it only calls tools, never executes code
        agent = ToolCallingAgent(
            tools=self.tools,
            model=self.model,
            max_steps=self.max_steps,  # Limit steps: understand -> generate -> execute
            verbosity_level=2
        )

        # Build enhanced task instructions
        task_instructions = self.instructions.format(task=task, schema_info=self.schema_info)
        
        try:
            result = agent.run(task_instructions)
            logger.info(f"Task completed...!")
            return result
        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            raise

    def run(self, task: str) -> str:
        """Run task with retry logic."""
        last_error = None
        
        for attempt in range(self.retries):
            try:
                return self._execute(task)
            except Exception as e:
                last_error = e
                logger.warning(f"Attempt {attempt + 1}/{self.retries} failed: {e}")
                if attempt < self.retries - 1:
                    logger.info("Retrying...")
        
        logger.error(f"All {self.retries} attempts failed")
        raise last_error


def main(task: Optional[str] = None) -> str:
    """Entry point for BehaviorAnalyzerAgent."""
    agent = BehaviorAnalyzerAgent()
    return agent.run(task)