from pydantic import BaseModel, Field
from typing import Optional, Any

class AgentRequest(BaseModel):
    """
    Request model for the orchestration agent.
    """
    task: str = Field(
        ..., 
        description="The task or query for the agent to execute in natural language.",
        example="Fetch attendance data then tell me who is the most late student."
    )
    conversation_id: Optional[str] = Field(
        None, 
        description="Optional conversation ID to maintain stateful context across multiple requests.",
        example="conv_12345"
    )

class AgentResponse(BaseModel):
    """
    Response model for the orchestration agent.
    """
    result: Any = Field(
        ..., 
        description="The detailed result of the agent's execution, usually as a string or structured data."
    )
    task: str = Field(
        ..., 
        description="The original task that was processed by the agent.",
        example="Fetch attendance data then tell me who is the most late student."
    )
    status: str = Field(
        "success", 
        description="The execution status (success/error).",
        example="success"
    )
