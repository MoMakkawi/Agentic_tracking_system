# Agentic Tracking System API

The **Agentic Tracking System API** is the backend application service responsible for collecting, processing, and validating student attendance logs. Built with **FastAPI**, it integrates rule-based anomaly validation, graph-based community detection (Louvain clustering), a persistent background scheduling service, and AI agent orchestration.

---

## Index

- [Overview](#overview)
- [Core Capabilities](#core-capabilities)
  - [Attendance Tracking](#attendance-tracking)
  - [Group Analytics](#group-analytics)
  - [Alert Management](#alert-management)
  - [Agent Integration](#agent-integration)
- [Event Scheduler](#event-scheduler)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [License](#license)

---

## Overview

The API serves as:
1. The **data engine** and query endpoint for the React frontend dashboard.
2. The **orchestration endpoint** for natural-language agent queries.
3. The **automation host** that aligns badge logs with scheduled calendar sessions and coordinates sub-agent execution workflows.

---

## Core Capabilities

### Attendance Tracking
* **Resource Ingestion**: Standardizes logs and calendar files.
* **Session Alignment**: Matches raw check-in sequences to scheduled events based on timestamps, device IDs, and participant identifiers.
* **Telemetry**: Computes session statistics such as total raw counts, unique attendee counts, and check-in timelines.

### Group Analytics
* **Cohort Clustering**: Leverages the Louvain community detection algorithm on participant similarity graphs.
* **Engagement Insights**: Exposes cohort-level stability indices, average check-in sizes, and group membership listings.

### Alert Management
Anomalies are flagged across three major categories to audit attendance integrity:
* **Device Alerts**: Logs hardware failures, missing logs metadata, clock synchronization issues, and sessions exceeding logical durations.
* **Timestamp Alerts**: Flags check-ins registered outside operating semesters, weekend check-ins, holiday scans, or check-ins outside daily limits.
* **Identity Alerts**: Detects invalid check-in formats, excessive duplicate scans (redundant check-ins), and globally rare or single-occurrence UIDs.

### Agent Integration
* Exposes `/agent/chat` endpoints for client dashboard queries.
* Routes queries to the central Orchestrator Agent.
* **Autonomous Invocations**: Integrates with the scheduler service to update cohorts and audit logs when calendar events conclude.

---

## Event Scheduler

The API runs a persistent **Event Scheduler Service** as a background thread:
- **Session Tracking**: Regularly polls the system `pass.ics` calendar to check if scheduled sessions have reached their ending time.
- **Precision Auditing**: Runs within a 60-second window (±30s) to guarantee no calendar events are missed due to polling frequencies.
- **Execution Safeguard**: Maintains a persistent record (`triggered_events.json`) to prevent duplicate pipelines from running for the same calendar event across application restarts.

---

## Running the Server

Start the FastAPI application server using:

```bash
python -m api.main
```

The server will initialize on `http://localhost:8000`.

---

## API Documentation

FastAPI generates Swagger and ReDoc documentation dynamically from Pydantic schemas:
- **Swagger UI**: Visit `http://localhost:8000/docs` to test, inspect, and trigger endpoints interactively.
- **ReDoc**: Visit `http://localhost:8000/redoc` for structured, readable API schemas.

---

## Project Structure

```text
api/
├── main.py          # FastAPI application initialization and startup events
├── constants.py     # Global variables and folder paths config
├── routers/         # REST endpoint routers (attendance, alerts, groups, agent)
├── services/        # Service managers (session managers, scheduler routines)
└── models/          # Pydantic validation schemas for endpoints
```

---

## License

See LICENSE in the project root.