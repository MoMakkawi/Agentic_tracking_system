import json
from typing import Dict, List, Any
from smolagents import tool
from utils import logger
from ..core.executor import Executor

# =========================================================
# Python Analysis Tool
# =========================================================
@tool
def execute_python_analysis_tool(code: str) -> str:
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
        execute_python_analysis_tool(code)
    """
    try:
        logger.info("Starting Python Analysis Tool...")
        executor = Executor()
        result = executor.execute_generated_code(code)
        logger.info("Python Analysis Tool finished successfully!")
        return str(result)

    except Exception as e:
        logger.error("Error in Python Analysis Tool", exc_info=True)
        return f"Error in execute_python_analysis_tool: {e}"