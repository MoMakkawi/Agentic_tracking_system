from smolagents.agents import ToolCallingAgent
from utils import logger, get_config, load_config
from utils import RagrennModel
from .tools import pipeline_agent_tool, validation_agent_tool, group_identifier_agent_tool, behavior_modeling_agent_tool 


class Orchestrator:
    """
    Orchestrator
    -----------------
    Coordinates multiple agents (pipeline, validation, group identification, behavior modeling) using SmolAgent tools.

    Features:
        - Executes complete pipeline, validation, identification, and modeling workflows
        - Delegates tasks to specialized sub-agents
        - Supports configurable instructions and retry logic
    """

    def __init__(self):
        load_config()
        config = get_config().LLM_MODULES.ORCHESTRATOR

        # Initialize model
        self.model = RagrennModel(model_config=config).to_smol_model()

        # Load orchestrator instructions
        self.instructions = config.INSTRUCTIONS
        self.retries = config.SETTINGS.RETRIES

        # Register tools
        self.tools = [pipeline_agent_tool, validation_agent_tool, group_identifier_agent_tool, behavior_modeling_agent_tool]

        logger.info("OrchestratorAgent initialized with tools: %s",
                    [t.name for t in self.tools])

    # ---------------------------------------------------------
    # Execute Task
    # ---------------------------------------------------------
    def _execute(self, task: str):
        logger.info(f"Executing orchestrator task: {task}")

        agent = ToolCallingAgent(
            tools=self.tools,
            model=self.model,
            instructions=self.instructions,
            add_base_tools=False
        )

        result = agent.run(task)
        logger.info("Orchestrator task completed successfully. Result: %s", result)
        return result

    # ---------------------------------------------------------
    # Run with Retries
    # ---------------------------------------------------------
    def run(self, task: str):
        for attempt in range(1, self.retries + 1):
            try:
                return self._execute(task)
            except Exception as e:
                logger.exception(f"Attempt {attempt} failed: {e}")
                if attempt == self.retries:
                    logger.error("All attempts failed for task: %s", task)
                    raise
                logger.info("Retrying orchestrator task...")


# ----------------------------
# main() entry-point
# ----------------------------
def main(task: str = None):
    orchestrator = Orchestrator()
    task = task or "Run full data pipeline and validate the results."
    result = orchestrator.run(task)
    return result


# ----------------------------
# CLI Usage
# ----------------------------
if __name__ == "__main__":
    output = main()
    print("\n=== Orchestrator Result ===")
    print(output)
