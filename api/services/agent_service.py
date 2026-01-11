"""
Agent service for business logic.

This module contains the AgentService class which handles the execution of tasks
via the Orchestrator agent.
"""

from typing import Optional
from agents import orchestrator_run
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
        from api.services.chat_service import ChatService
        self.chat_service = ChatService()
    
    def run_task(self, task: Optional[str] = None, conversation_id: Optional[str] = None) -> AgentResponse:
        """
        Run a task using the Orchestrator agent.
        
        Args:
            task: The task to be executed by the agent.
            conversation_id: Optional conversation ID to maintain memory.
            
        Returns:
            AgentResponse containing the result and status.
        """
        
        try:
            history = None
            if conversation_id:
                conversation = self.chat_service.get_conversation(conversation_id)
                if conversation:
                    history = conversation.messages
            
            result = orchestrator_run(task, history=history)
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
