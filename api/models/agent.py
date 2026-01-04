from pydantic import BaseModel, Field
from typing import Optional, Any

class AgentRequest(BaseModel):
    """
    Request model for the orchestration agent.
    """
    task: str = Field(..., description="The task or query for the agent to execute")

class AgentResponse(BaseModel):
    """
    Response model for the orchestration agent.
    """
    result: Any = Field(..., description="The result of the agent's execution")
    task: str = Field(..., description="The original task that was executed")
    status: str = Field("success", description="The status of the execution")
