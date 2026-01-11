# Agentic Tracking System API

## Index

- [Overview](#overview)
- [Core Capabilities](#core-capabilities)
  - [Attendance Tracking](#attendance-tracking)
  - [Group Analytics](#group-analytics)
  - [Alert Management](#alert-management)
  - [Agent Integration](#agent-integration)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview

The **Agentic Tracking System API** is the central backend service responsible for collecting, processing, and analyzing student attendance data. It enables intelligent insights into academic behavior by combining rule-based validation, graph-based group analytics, and agent-driven orchestration.

This API serves as:
- The **data processing backbone** for the frontend dashboard.
- The **execution layer** for agentic workflows and orchestration.
- The **decision-support system** for academic integrity and behavioral analysis.

---

## Core Capabilities

### Attendance Tracking

- Ingests and standardizes raw attendance logs from multiple sources.
- Matches attendance sessions using multi-factor identification:
  - Timestamp
  - Device ID
  - User identifiers (UIDs)
- Detects:
  - Duplicate check-ins
  - Redundant sessions
  - Abnormal attendance patterns

---

### Group Analytics

- Identifies student communities using **Louvain community detection** on interaction graphs.
- Analyzes:
  - Collaborative behavior
  - Attendance similarity
  - Long-term group stability
- Supports filtering and evaluation of groups based on:
  - Size
  - Composition
  - Behavioral coherence

---

### Alert Management

The alerting subsystem flags suspicious or invalid activity through specialized alert categories:

- **Device Alerts**
  - Invalid or inconsistent device usage.
  - Repeated device anomalies across sessions.

- **Identity Alerts**
  - Suspicious UID behavior.
  - Potential identity spoofing or misuse.

- **Timestamp Alerts**
  - Time-based inconsistencies.
  - Impossible or conflicting session timelines.

---

### Agent Integration

- Exposes dedicated `/agent` endpoints for the **Orchestration Agent**.
- Enables:
  - Natural language task execution.
  - Delegation to specialized sub-agents.
  - Coordinated multi-step analytical workflows.
- Designed to support extensible agentic reasoning and automation.

---

## Running the Server

Start the FastAPI development server using:

```bash
python -m api.main
```

Once the server is running, the API is accessible at: `http://0.0.0.0:8000`

---

## API Documentation

Comprehensive API documentation is generated automatically from the source code and kept in sync with the implementation:

- **Swagger UI**  
  `http://localhost:8000/docs`  
  Interactive interface for exploring, testing, and validating API endpoints.

- **ReDoc**  
  `http://localhost:8000/redoc`  
  Structured, human-readable reference documentation optimized for clarity.

---

## Project Structure

```text
api/
├── routers/     # API endpoint definitions (Attendance, Alerts, Groups, Agents)
├── services/    # Core business logic and data processing layers
├── models/      # Pydantic schemas for request and response validation
├── constants.py # Shared constants and system configuration
└── main.py      # FastAPI application entry point and setup
```

---

## License

See LICENSE in project root