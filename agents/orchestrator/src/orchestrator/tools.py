from smolagents import tool
from agents.sub_agents import *
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
        2. Fetches, preprocesses.
        3. Returns the final processed dataset path or summary.

    Args:
        task (str, optional): Task description (default task will be used if None).

    Returns:
        str: Path to processed data or summary message.
    """
    try:
        logger.info("[Orchestrator] Invoking DataPipelineAgent...")
        result = data_pipeline_main(task)
        logger.info("DataPipelineAgent completed successfully.")
        return str(result) if result is not None else "Task completed but returned no result."
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
        result = data_validation_main(task)
        logger.info("DataValidationAgent completed successfully.")
        return str(result) if result is not None else "Task completed but returned no result."
    except Exception as e:
        logger.exception("Validation agent tool failed.")
        return f"Error in validation_agent_tool: {e}"

@tool
def group_identifier_agent_tool(task: str = None) -> str:
    """
    Orchestrates the GroupIdentifierAgent.

    Workflow:
        1. Runs the GroupIdentifierAgent to identify student groups.
        2. Can answer questions like "Find the IoT MSc group".
        3. Returns the result or summary.

    Args:
        task (str, optional): Task description (default task will be used if None).

    Returns:
        str: Result of group identification or summary message.
    """
    try:
        logger.info("[Orchestrator] Invoking GroupIdentifierAgent...")
        result = group_identification_main(task)
        logger.info("GroupIdentifierAgent completed successfully.")
        return str(result) if result is not None else "Task completed but returned no result."
    except Exception as e:
        logger.exception("Group identifier agent tool failed.")
        return f"Error in group_identification_agent_tool: {e}"

@tool
def insightater_agent_tool(task: str = None) -> str:
    """
    Orchestrates the KnowledgeInsightAgent.

    Workflow:
        1. Runs the KnowledgeInsightAgent to analyze attendance behavior.
        2. Generates python code to analyze data.
        3. Returns the analysis result or summary.

    Args:
        task (str, optional): Task description (default task will be used if None).

    Returns:
        str: Result of behavior analysis or summary message.
    """
    try:
        logger.info("[Orchestrator] Invoking KnowledgeInsightAgent...")
        result = knowledge_insight_main(task)
        logger.info("KnowledgeInsightAgent completed successfully.")
        return str(result) if result is not None else "Task completed but returned no result."
    except Exception as e:
        logger.exception("Behavior modeling agent tool failed.")
        return f"Error in insightater_agent_tool: {e}"