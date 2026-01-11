from fastapi import APIRouter, HTTPException, Depends
from api.models import AgentRequest, AgentResponse
from api.services import AgentService
from utils import logger

router = APIRouter()

def get_agent_service() -> AgentService:
    """Dependency injection for AgentService."""
    return AgentService()

@router.post(
    "/run",
    response_model=AgentResponse,
    summary="Run Agent Task",
    description="Send a natural language task to the orchestration agent.",
    responses={
        500: {"description": "Agent execution failed"}
    }
)
async def run_agent_task(
    request: AgentRequest,
    service: AgentService = Depends(get_agent_service)
):
    """
    Run a task using the Orchestration Agent.
    
    This endpoint allows you to send a natural language task to the 
    orchestration agent, which will coordinate sub-agents to complete it.
    """
    logger.info(f"API request to run agent task: {request.task}")
    
    try:
        response = service.run_task(request.task, conversation_id=request.conversation_id)
        if response.status == "error":
            raise HTTPException(status_code=500, detail=response.result)
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in agent router: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")