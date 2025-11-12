from smolagents import tool
from data_pipeline import main as data_pipeline_agent_main
from data_validation import main as data_validation_agent_main
from utils import logger

# -------------------------------
# Tool Definitions
# -------------------------------

@tool
def pipeline_agent_tool(task: str = None) -> str:
    """
    Orchestrates the DataPipelineAgent.

    Workflow:
        1. Runs the DataPipelineAgent end-to-end.
        2. Fetches, preprocesses, and groups data.
        3. Returns the final processed dataset path or summary.

    Args:
        task (str, optional): Task description (default task will be used if None).

    Returns:
        str: Path to processed data or summary message.
    """
    try:
        logger.info("[Orchestrator] Invoking DataPipelineAgent...")
        result = data_pipeline_agent_main(task)
        logger.info("DataPipelineAgent completed successfully.")
        return str(result)
    except Exception as e:
        logger.exception("Pipeline agent tool failed.")
        return f"Error in pipeline_agent_tool: {e}"

@tool
def validation_agent_tool(task: str = None) -> str:
    """
    Orchestrates the DataValidationAgent.

    Workflow:
        1. Runs the DataValidationAgent on processed data.
        2. Performs timestamp, device, and identity validation.
        3. Returns a validation report or summary.

    Args:
        task (str, optional): Validation description (default if None).

    Returns:
        str: Path to validation report or summary message.
    """
    try:
        logger.info("[Orchestrator] Invoking DataValidationAgent...")
        result = data_validation_agent_main(task)
        logger.info("DataValidationAgent completed successfully.")
        return str(result)
    except Exception as e:
        logger.exception("Validation agent tool failed.")
        return f"Error in validation_agent_tool: {e}"