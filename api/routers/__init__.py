from .attendance import router as attendance_router
from .alerts import router as alerts_router
from .groups import router as groups_router
from .agent import router as agent_router
from .chat import router as chat_router
from .analytics import router as analytics_router

__all__ = [
    "attendance_router",
    "alerts_router",
    "groups_router",
    "agent_router",
    "chat_router",
    "analytics_router",
]

