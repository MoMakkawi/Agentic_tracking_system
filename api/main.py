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
from utils import load_config, get_config

app = FastAPI(
    title="Agentic Tracking System API",
    description="""
    # Agentic Tracking System API
    
    This API provides the backend services for the Agentic Tracking System.
    
    ## Key Features
    * **Attendance Tracking**: Monitor and manage session data.
    * **Group Analytics**: Analyze group dynamics and identification.
    * **Alerts**: System notifications and anomaly detection.
    * **Agent Interaction**: specific endpoints for the orchestrator agent and sub-agents.
    
    ## Authentication
    Currently open (internal use).
    """,
    version="0.2.0",
    contact={
        "name": "API Support",
        "url": "http://localhost:8000/docs",
    },
    openapi_tags=[
        {"name": "Attendance", "description": "Operations with attendance sessions and statistics."},
        {"name": "Alerts", "description": "Manage system alerts and notifications."},
        {"name": "Groups", "description": "Group identification and analytics."},
        {"name": "Agent", "description": "Agent orchestrator control and status."},
        {"name": "Chat", "description": "Chat interface for communicating with the agent."},
        {"name": "Analytics", "description": "Data analytics and reporting."},
    ]
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

@app.get("/")
def root():
    return {"message": "Welcome to the Agentic Tracking System API. Visit /docs for Swagger UI."}

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

