# Agents

Core multi-agent system that orchestrates data processing, validation, grouping, and analytical insights for student attendance tracking.

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
  - [Running Tests](#running-tests)
- [Configuration](#configuration)
- [Error Handling](#error-handling)
- [Monitoring & Logging](#monitoring--logging)
- [License](#license)


## Overview

The agents module implements a hierarchical agent architecture where:
- **Orchestrator Agent** acts as the central controller, parsing user requests or autonomous system triggers and delegating tasks
- **Sub-agents** handle specialized responsibilities with narrow, well-defined scopes
- Each agent is modular, testable, and reusable across different contexts

## Architecture

```
Orchestrator Agent (Entry Point)
└── Sub Agents
    ├── Data Pipeline Agent
    │   ├── Data Fetcher
    │   ├── Preprocessor
    │   └── Session Builder
    ├── Data Validation Agent
    │   ├── Device Validator
    │   ├── Timestamp Validator
    │   └── Identity Validator
    ├── Group Identifier Agent
    │   ├── Feature Engineer
    │   ├── Louvain Clustering
    │   └── Group Analyzer
    └── Knowledge Insight Agent
        ├── Query Analyzer
        ├── Code Generator
        └── Safe Executor
Shared Components
└── Memory Package (Short-term, Long-term)
```

## Components

### orchestrator/

Central entry point that receives user queries and coordinates execution across sub-agents.

**Responsibilities:**
- Parse and classify user requests
- Design execution workflows
- Aggregate results into coherent responses
- Handle errors and graceful degradation

### sub_agents/

Specialized agents, each handling a specific domain of the tracking system.

#### data_pipeline/

Handles raw data ingestion, cleaning, and preprocessing.

- **Fetch**: Retrieves attendance records and schedules from data sources
- **Clean**: Removes duplicates, handles missing values, normalizes formats
- **Build Sessions**: Constructs cleaned session objects with metadata

#### data_validation/

Runs multi-layer validation to detect anomalies and inconsistencies.

- **Device Validation**: Checks for suspicious device patterns
- **Timestamp Validation**: Identifies impossible or illogical timestamps
- **Identity Validation**: Verifies student identity consistency

#### group_identifier/

Build behavioral groups through clustering analysis.

- **Feature Engineering**: Creates behavioral features from sessions
- **Clustering**: Applies Louvain algorithm to identify student communities
- **Group Analysis**: Characterizes groups by patterns and attributes

#### knowledge_insight/

Generates custom analytical insights through safe code execution.

- **Query Understanding**: Parses natural language analysis requests
- **Code Generation**: Creates safe Python analysis snippets
- **Execution**: Runs code with resource limits and safety checks

### memory/

Shared memory package providing persistence capabilities for agents.

- **Short-Term Memory**: Conversation history and context management
- **Long-Term Memory**: Persistent storage across sessions (planned)
- **Memory Manager**: Coordinator for multiple memory types

## Workflow Example

### User Query: "What are the attendance patterns of students in group 2?"

1. **Orchestrator** receives query
2. validates scope and safety
3. interprets user intent
4. designs execution plan
5. selects and orders required sub-agents
6. dispatches agents sequentially
7. monitors failures and adapts safely
8. synthesizes final user-facing response

Note : Orchestrator have short memory, so it will not remember previous conversations that will help him to understand the context of the conversation and sometime will use it is memory to help him to answer the user query or to plan the execution of the sub-agents.

## Getting Started

### Basic Usage

```python
from agents.orchestrator import orchestrator_run

response = orchestrator_run("Show me abnormal attendance patterns.")
print(response)
```
## Configuration

Each agent reads from `config.json`:

## Error Handling

Agents implement graceful degradation:

- **Critical Errors**: Stop execution, return error details
- **Warning Errors**: Continue with partial results, log warning
- **Data Errors**: Fallback to cached data or defaults

All errors are logged with full context for debugging.

## Monitoring & Logging

All agents log to `logs/agents.log`:

```
2026-01-11 16:09:55 | run.py | INFO |       AGENTIC TRACKING SYSTEM - DASHBOARD & API
2026-01-11 16:09:56 | run.py | INFO | Starting API on http://localhost:8000...
2026-01-11 16:09:56 | run.py | INFO | Starting Dashboard...
2026-01-11 16:09:56 | run.py | INFO | Both services are starting. Press Ctrl+C to stop both.
2026-01-11 16:10:12 | api\services\session_service.py | INFO | Loading all sessions and detailed alerts
2026-01-11 16:10:13 | api\services\session_service.py | INFO | Loaded 101 sessions with detailed alerts successfully
```

## License
See LICENSE in project root