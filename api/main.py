from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from pathlib import Path

from .routers import (
    attendance_router, 
    alerts_router, 
    groups_router, 
    agent_router, 
    chat_router, 
    analytics_router
)
from .services import get_scheduler
from utils import load_config, get_config

# Initialize scheduler (lazy, won't start until lifespan)
scheduler = get_scheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager.
    Starts the event scheduler on startup and stops it on shutdown.
    """
    # Startup
    await scheduler.start()
    yield
    # Shutdown
    await scheduler.stop()


app = FastAPI(
    title="Agentic Tracking System (ATS) API",
    description="""
    ## Overview
    The **Agentic Tracking System (ATS)** is a professional-grade attendance analytics platform. 
    This API serves as the backbone for the system, providing endpoints for data management, 
    AI agent orchestration.

    ## Modules
    * **Attendance**: Manage and analyze session-level attendance logs.
    * **Alerts**: Access security and data integrity anomalies.
    * **Groups**: Explore student clusters identified by AI analysis.
    * **Agent & Chat**: Interact with the **Orchestrator Agent** for natural language queries.

    ## Usage Notes
    * **Pagination**: Lists are paginated by default. Page indices start at 1.
    * **Sorting**: Use `order_by` and `order_direction` (asc/desc) for data ordering.
    * **Authentication**: Currently restricted to internal network use.
    """,
    version="0.3.0",
    contact={
        "name": "ATS Development Team",
        "url": "http://localhost:5173/about",
        "email": "MoMakkawi@hotmail.com",
    },
    license_info={
        "name": "Proprietary",
    },
    openapi_tags=[
        {
            "name": "Attendance", 
            "description": "Session monitoring, log retrieval, and attendance statistics.",
            "externalDocs": {
                "description": "Dashboard",
                "url": "http://localhost:5173/attendance",
            },
        },
        {"name": "Alerts", "description": "Anomaly detection reports (Identity, Timestamp, Device)."},
        {"name": "Groups", "description": "AI-driven student grouping and cohort analysis."},
        {"name": "Agent", "description": "Natural language task orchestration and agent control."},
        {"name": "Chat", "description": "Interactive conversation management with the AI agent."},
        {"name": "Analytics", "description": "High-level reporting and data insights."},
    ],
    lifespan=lifespan,
)


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(attendance_router, prefix="/attendance", tags=["Attendance"])
app.include_router(alerts_router, prefix="/alerts", tags=["Alerts"])
app.include_router(groups_router, prefix="/groups", tags=["Groups"])
app.include_router(agent_router, prefix="/agent", tags=["Agent"])
app.include_router(chat_router, prefix="/chat", tags=["Chat"])
app.include_router(analytics_router, prefix="/analytics", tags=["Analytics"])

def run_server():
    load_config()

    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    run_server()

