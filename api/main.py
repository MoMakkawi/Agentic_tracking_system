from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from pathlib import Path

from .routers import attendance_router, alerts_router, groups_router, agent_router, chat_router
from utils import load_config, get_config

app = FastAPI(title="Agentic Tracking System API", version="0.2.0")

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

