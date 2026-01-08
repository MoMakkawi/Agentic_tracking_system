from smolagents import tool
from agents.sub_agents import *
from utils import logger

# -------------------------------
# Tool Definitions
# -------------------------------

@tool
def pipeline_agent_tool(task: str = None) -> str:
    """
    Orchestrates the Data Pipeline Agent by fetching and preprocessing data.

    Workflow:
        1. Runs the Data Pipeline Agent end-to-end.
        2. Only fetches, preprocesses data.
        3. Returns confirmation message if every thing done correctly (Dont mention to the paths that we save the data in).

    Args:
        task (str, optional): Task description (default task will be used if None).

    Returns:
        str: confirmation message mention the the task that done.
    """
    try:
        logger.info("[Orchestrator] Invoking DataPipelineAgent...")
        result = data_pipeline_main(task)
        logger.info("DataPipelineAgent completed successfully.")
        return result
    except Exception as e:
        logger.exception("Pipeline agent tool failed.")
        return f"Error in pipeline_agent_tool: {e}"

@tool
def validation_agent_tool(task: str = None) -> str:
    """
    Orchestrates the Data Validation Agent to validate the data.

    Workflow:
        1. Runs the Data Validation Agent end-to-end.
        2. Performs timestamp, device, and identity validation.
        3. Returns confirmation message if every thing done correctly (Dont mention to the paths that we save the data in).

    Args:
        task (str, optional): Validation description (default if None).

    Returns:
        str: confirmation message if every thing done correctly (Dont mention to the paths that we save the data in).
    """
    try:
        logger.info("[Orchestrator] Invoking DataValidationAgent...")
        result = data_validation_main(task)
        logger.info("DataValidationAgent completed successfully.")
        return result
    except Exception as e:
        logger.exception("Validation agent tool failed.")
        return f"Error in validation_agent_tool: {e}"

@tool
def group_identifier_agent_tool(task: str = None) -> str:
    """
    Orchestrates the Group Identifier Agent to identify student groups and usually dont used for the queries about groups.

    Workflow:
        1. Runs the Group Identifier Agent end-to-end.
        2. Returns confirmation message if every thing done correctly (Dont mention to the paths that we save the data in).

    Args:
        task (str, optional): Task description (default task will be used if None).

    Returns:
        str: confirmation message if every thing done correctly (Dont mention to the paths that we save the data in).

    """
    try:
        logger.info("[Orchestrator] Invoking GroupIdentifierAgent...")
        result = group_identification_main(task)
        logger.info("GroupIdentifierAgent completed successfully.")
        return result
    except Exception as e:
        logger.exception("Group identifier agent tool failed.")
        return f"Error in group_identification_agent_tool: {e}"

@tool
def insighter_agent_tool(task: str = None) -> str:
    """
    Orchestrates the Knowledge Insight Agent to analyze attendance behavior / groups / alerts / etc.

    Workflow:
        1. Runs the Knowledge Insight Agent end-to-end.
        2. Generates python code to answer any queries.
        3. Returns the analysis result or summary.

    Args:
        task (str, optional): Task description (default task will be used if None).

    Returns:
        str: Result of analysis or summary message.
    """
    try:
        logger.info("[Orchestrator] Invoking KnowledgeInsightAgent...")
        result = knowledge_insight_main(task)
        logger.info("KnowledgeInsightAgent completed successfully.")
        return result
    except Exception as e:
        logger.exception("Behavior modeling agent tool failed.")
        return f"Error in insightater_agent_tool: {e}"