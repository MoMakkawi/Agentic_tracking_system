import json
from typing import Dict, List, Any
from smolagents import tool
from utils import logger
from ..core.clean_data_insighter import CleanDataInsighter
from ..core.groups_insighter import GroupInsighter

# =========================================================
# Clean Data Insight Tool
# =========================================================
@tool
def clean_data_insighter_tool(code: str) -> str:
    """
    Execute Python analysis code in a controlled environment.

    This tool receives Python code as a string and executes it safely.
    The execution environment provides:
    - attendance_data: list of session dictionaries
    - is_valid_id(uid): function to validate user IDs
    - Pre-imported modules: statistics, collections, datetime, json

    Args:
        code (str): Python code string to execute. Must assign result to 'result' variable.

    Returns:
        str: Execution result or error message

    Example:
        code = '''
        filtered = [s for s in attendance_data if s.get('status') == 'late']
        result = len(filtered)
        '''
        clean_data_insighter_tool(code)
    """
    try:
        logger.info("Starting Clean Data Insight Tool...")
        executor = CleanDataInsighter()
        result = executor.execute(code)
        logger.info("Clean Data Insight Tool finished successfully!")
        return str(result)

    except Exception as e:
        logger.error("Error in Clean Data Insight Tool", exc_info=True)
        return f"Error in clean_data_insighter_tool: {e}"


# =========================================================
# Group Insight Tool
# =========================================================
@tool
def groups_insighter_tool(code: str) -> str:
    """
    Execute Python analysis code in a controlled environment.

    This tool receives Python code as a string and executes it safely.
    The execution environment provides:
    - groups_data: list of group dictionaries
    - Pre-imported modules: statistics, collections, datetime, json

    Args:
        code (str): Python code string to execute. Must assign result to 'result' variable.

    Returns:
        str: Execution result or error message

    Example:
        code = '''
        filtered = {g: len(members) for g, members in groups_data.items()}
        result = filtered
        '''
        group_insighter_tool(code)
    """
    try:
        logger.info("Starting Groups Insight Tool...")
        executor = GroupInsighter()
        result = executor.execute(code)
        logger.info("Groups Insight Tool finished successfully!")
        return str(result)

    except Exception as e:
        logger.error("Error in Groups Insight Tool", exc_info=True)
        return f"Error in groups_insighter_tool: {e}"