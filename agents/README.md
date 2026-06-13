# Agents Package

Core multi-agent intelligence layer of the **Agentic Tracking System**. This package orchestrates data ingestion, rule-based validation, graph-based clustering, and natural-language insight generation using the **smolagents** framework.

---

## Index

- [Overview](#overview)
- [Architecture](#architecture)
- [Components](#components)
  - [orchestrator](#orchestrator)
  - [sub_agents](#sub_agents)
    - [data_pipeline](#data_pipeline)
    - [data_validation](#data_validation)
    - [group_identifier](#group_identifier)
    - [knowledge_insight](#knowledge_insight)
  - [memory](#memory)
- [Workflow Example](#workflow-example)
- [Getting Started](#getting-started)
  - [Installation](#installation)
  - [Basic Usage](#basic-usage)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Monitoring & Logging](#monitoring--logging)
- [License](#license)

---

## Overview

The `agents` package implements a hierarchical agent workflow:
- **Orchestrator Agent**: Acts as the central controller, scope validator, routing planner, and final response composer. It receives user inputs or system events and delegates work to sub-agents.
- **Sub-Agents**: Specialized units with a narrow, well-defined scope (validation, ingestion, grouping, or analysis).
- **Context Preservation**: Employs an isolated memory layer to track conversation states without leaks.

---

## Architecture

```text
Orchestrator Agent (Entry Point & Planner)
└── Sub-Agents
    ├── Data Pipeline Agent (Stage 1)
    │   ├── Ingests raw badge logs & calendar files
    │   └── Standardizes and structures data into clean sessions
    ├── Data Validation Agent (Stage 2)
    │   ├── Performs Device validation (clock resets, duration)
    │   ├── Performs Timestamp validation (valid dates, holiday checks)
    │   └── Performs Identity validation (hex patterns, redundancy)
    ├── Group Identifier Agent (Stage 3)
    │   ├── Generates student co-attendance features
    │   └── Applies Louvain clustering to identify cohort communities
    └── Knowledge Insight Agent (Stage 4)
        ├── Analyzes natural-language queries
        └── Generates and executes sandboxed Python code over datasets

Shared Core
└── Memory System (Short-term, session-isolated memory manager)
```

---

## Components

### orchestrator/
The master control agent.
* **Responsibilities**:
  * Validates whether user queries are within the allowed analytics scope.
  * Checks existing memory context using an **Insight-First** resolution policy.
  * Dispatches sub-agents with goal-level descriptions instead of technical details (hiding paths/tools).
  * Cleans and formats sub-agent results into a polite, professional final answer.

### sub_agents/
Specialized computational and reasoning agents.

#### data_pipeline/
* **Purpose**: Fetches, cleans, and standardizes data.
* **Responsibilities**: Downloads raw logs and calendar resources, deduplicates check-ins, and creates structured session objects.

#### data_validation/
* **Purpose**: Performs quality assurance checks.
* **Responsibilities**: Executes device, timestamp, and identity validations to flag data corruption and potential check-in spoofing.

#### group_identifier/
* **Purpose**: Clusters participants based on behavior.
* **Responsibilities**: Extracts features and runs the Louvain algorithm to partition participants into engagement cohorts.

#### knowledge_insight/
* **Purpose**: Generates interactive query results.
* **Responsibilities**: Receives target analytical questions, generates appropriate Python scripts, and runs them securely inside a restricted sandbox environment.

### memory/
* **Purpose**: Maintains conversation history.
* **Responsibilities**: Provides chat-scoped short-term memory to keep track of user context within a session, preventing prompt injection across sessions.

---

## Workflow Example

### User Query: "Are there any anomalies in Group 2's attendance?"

1. **Orchestrator** receives the query and validates that it falls within the allowed attendance scope.
2. It checks its **Short-Term Memory** to see if relevant context was recently loaded.
3. If fresh data is required, it plans the execution sequence and invokes sub-agents.
4. It calls **Knowledge Insight** with instructions to evaluate Group 2 against security alert logs.
5. The sub-agent generates a sandboxed script, executes it, and returns the list of anomalies.
6. The Orchestrator improves formatting, removes raw tracebacks, and delivers a clean final summary to the user.

> **Note**: The Orchestrator leverages a short-term memory system to maintain conversation context across multiple turns, enabling context-aware interactions and avoiding redundant computations by reusing past insights.

---

## Getting Started

### Installation

Install all agent modules in editable mode from the root directory:

```bash
pip install -e ./agents/orchestrator -e ./agents/sub_agents/data_pipeline -e ./agents/sub_agents/data_validation -e ./agents/sub_agents/group_identification -e ./agents/sub_agents/knowledge_insight
```

### Basic Usage

You can invoke the orchestrator directly from Python:

```python
from agents.orchestrator import orchestrator_run

# Execute query
response = orchestrator_run("Show me the total check-in count for the last session.")
print(response)
```

---

## Configuration

All agents load configuration details dynamically from the global `config.json` file. Each agent reads settings under its respective key in the `LLM_MODULES` section:
* **LLM Model Families**: Defines primary and fallback models (e.g. OpenAI, Mistral, Llama, codestral).
* **Retry Policies**: Configures execution retries for API resilience.
* **Module-Specific Parameters**: Such as similarity thresholds for Louvain clustering and AST execution limitations for knowledge insights.

---

## Error Handling

The package enforces strict execution safety policies:
* **Fail-Closed Principle**: If a scope violation or potential prompt injection is detected, the query is rejected immediately with a canonical warning message.
* **Sub-Agent Halting**: In multi-agent pipelines, any failure in a step (e.g., pipeline ingestion fails) halts the chain immediately to prevent processing stale or corrupt records.
* **Graceful Degradation**: User-facing responses summarize errors at a high level and hide detailed raw tracebacks for system safety.

---

## Monitoring & Logging

Execution telemetry is managed by the structured logger in `utils`. Logs are written directly to standard output and persisted on disk:
* **Agents Telemetry**: Located at `logs/agents.log` (or output path defined in config), recording tool execution times, prompt tokens, and validation status.
* **Server Logs**: Tracks API calls and event scheduler status (e.g. tracking concluded calendar events and auto-triggering workflows).

---

## License

See LICENSE in the project root.