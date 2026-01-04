"""
Agent service for business logic.

This module contains the AgentService class which handles the execution of tasks
via the Orchestrator agent.
"""

from typing import Optional
from agents.orchestrator import orchestrator_main
from utils import logger
from api.models import AgentResponse

class AgentService:
    """
    Service class for agent-related business logic.
    """
    
    def __init__(self):
        """
        Initialize the AgentService and the Orchestrator.
        """
    
    def run_task(self, task: Optional[str] = None) -> AgentResponse:
        """
        Run a task using the Orchestrator agent.
        
        Args:
            task: The task to be executed by the agent.
            
        Returns:
            AgentResponse containing the result and status.
        """
        logger.info(f"AgentService received task: {task}")
        
        try:
            result = orchestrator_main(task)
            return AgentResponse(
                result=result,
                task=task,
                status="success"
            )
        except Exception as e:
            logger.error(f"Error running agent task: {str(e)}")
            return AgentResponse(
                result=str(e),
                task=task or "unknown",
                status="error"
            )
