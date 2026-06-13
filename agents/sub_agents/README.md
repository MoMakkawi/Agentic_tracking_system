# Sub-Agents Package

The `sub_agents` package contains specialized agent modules that form the **multi-stage pipeline** of the Agentic Tracking System. Each agent operates independently with a single responsibility, processing and refining data for the next stage in a deterministic, composable sequence.

---

## Index

- [Overview](#overview)
- [Architecture](#architecture)
- [Agents](#agents)
  - [Data Pipeline Agent – Stage 1](#1-data-pipeline-agent--stage-1)
  - [Data Validation Agent – Stage 2](#2-data-validation-agent--stage-2)
  - [Group Identifier Agent – Stage 3](#3-group-identifier-agent--stage-3)
  - [Knowledge Insight Agent – Stage 4](#4-knowledge-insight-agent--stage-4)
- [Package Structure](#package-structure)
- [Installation](#installation)
- [Usage](#usage)
  - [Importing Agents](#importing-agents)
  - [Running the Pipeline](#running-the-pipeline)
- [Default Data Flow](#default-data-flow)
- [Key Design Principles](#key-design-principles)
- [Configuration](#configuration)
- [Development](#development)
- [License](#license)

---

## Overview

Dividing the system into four independent sub-agents ensures that validation logic, graph-clustering logic, and natural-language execution logic do not cross-cut. This design prevents cascading errors and allows developers to test, upgrade, and deploy individual pipeline stages independently.

---

## Architecture

The system executes data processing in a **sequential 4-stage architecture**:

```
Source URLs → [Stage 1: Pipeline] → [Stage 2: Validation] → [Stage 3: Grouping] → [Stage 4: Analysis] → Insights
```

Each stage is characterized by:
- **Single Responsibility**: One task, isolated from downstream or upstream concerns.
- **Strict I/O Contract**: Explicit file paths and schemas read from `config.json`.
- **Tool-Based Execution**: Isolated model actions using registered, single-purpose tools.

---

## Agents

### 1. Data Pipeline Agent – Stage 1
* **Module**: `data_pipeline`
* **Purpose**: Raw data ingestion, file downloading, and log cleaning.
* **Responsibilities**:
  * Downloads `.ics` calendar events and `.jsonl` attendance logs from source URLs.
  * Standardizes raw logs, deduplicates duplicate scans, and aggregates them into structured session blocks.
  * Enriches sessions with overlapping calendar schedules (subject titles, start/end windows).
* **Key Constraint**: No validation or clustering; purely handles extraction, parsing, and cleaning.
* **Tools**: `fetch_tool`, `preprocess_tool`.
* **Output**: A cleaned sessions dataset stored in JSON.
* **Documentation**: See [`data_pipeline/README.md`](./data_pipeline/README.md).

### 2. Data Validation Agent – Stage 2
* **Module**: `data_validation`
* **Purpose**: Data quality auditing and anomaly logging.
* **Responsibilities**:
  * Scans preprocessed sessions to detect device-level errors (duration errors, clock resets).
  * Audits timestamps for logical consistency (weekend check-ins, out-of-bounds check-ins).
  * Validates identity compliance (UID formats, redundancy metrics, rare check-in logs).
* **Key Constraint**: No cohort clustering or analytical interpretations; validation only.
* **Tools**: `device_validation_tool`, `timestamp_validation_tool`, `identity_validation_tool`.
* **Output**: Separate Device, Identity, and Timestamp CSV alerts.
* **Documentation**: See [`data_validation/README.md`](./data_validation/README.md).

### 3. Group Identifier Agent – Stage 3
* **Module**: `group_identification`
* **Purpose**: Cohort discovery and community detection.
* **Responsibilities**:
  * Converts student co-attendance patterns into feature vectors.
  * Creates similarity graphs and runs the Louvain community detection algorithm.
  * Saves assignments to standard groups mapping files.
* **Key Constraint**: Does not handle validation or answer queries; clustering and persistence only.
* **Tools**: `louvain_clustering_tool`, `save_tool`.
* **Output**: Persistent group mapping JSON files.
* **Documentation**: See [`group_identification/README.md`](./group_identification/README.md).

### 4. Knowledge Insight Agent – Stage 4
* **Module**: `knowledge_insight`
* **Purpose**: Sandboxed analytics execution and response formulation.
* **Responsibilities**:
  * Parses incoming natural-language analytics requests.
  * Generates a safe Python script addressing the query.
  * Executes the code securely inside a restricted sandbox namespace against preloaded datasets.
* **Key Constraint**: Read-only access; works exclusively on preprocessed and grouped datasets.
* **Tools**: `data_insighter_tool`, `groups_insighter_tool`, `alerts_insighter_tool`.
* **Output**: A synthesized response string.
* **Documentation**: See [`knowledge_insight/README.md`](./knowledge_insight/README.md).

---

## Package Structure

```text
sub_agents/
├── data_pipeline/              # Stage 1: Data Ingestion & Preprocessing
│   ├── src/data_pipeline/      # Python source files
│   ├── README.md               # Stage 1 documentation
│   ├── __init__.py
│   └── pyproject.toml
├── data_validation/            # Stage 2: Anomaly Validation Checks
│   ├── src/data_validation/
│   ├── README.md
│   ├── __init__.py
│   └── pyproject.toml
├── group_identification/       # Stage 3: Cohort Clustering
│   ├── src/group_identification/
│   ├── README.md
│   ├── __init__.py
│   └── pyproject.toml
├── knowledge_insight/          # Stage 4: Sandboxed Analytics
│   ├── src/knowledge_insight/
│   ├── README.md
│   ├── __init__.py
│   └── pyproject.toml
└── __init__.py                 # Sub-Agents package entry points
```

---

## Installation

Install the entire sub-agents package in editable mode from the root workspace:

```bash
pip install -e ./agents/sub_agents/data_pipeline -e ./agents/sub_agents/data_validation -e ./agents/sub_agents/group_identification -e ./agents/sub_agents/knowledge_insight
```

---

## Usage

### Importing Agents

```python
from agents.sub_agents import (
    data_pipeline_main,
    data_validation_main,
    group_identification_main,
    knowledge_insight_main
)
```

### Running the Pipeline

The agents are orchestrated by the Orchestrator but can also be executed programmatically:

```python
# Stage 1: Fetch raw resources and preprocess logs
pipeline_status = data_pipeline_main("Fetch and preprocess raw logs.")

# Stage 2: Audit preprocessed sessions for anomalies
validation_status = data_validation_main("Audit logs and write anomaly reports.")

# Stage 3: Recompute Louvain community cohorts
grouping_status = group_identification_main("Group students by co-attendance patterns.")

# Stage 4: Run target analysis queries
analytical_result = knowledge_insight_main("List all groups with at-risk students.")
```

---

## Default Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│             Input: .ics & .logs URLs from config.json           │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│          Stage 1: Data Pipeline (Ingestion & Preprocessing)     │
│                   Outputs: Clean Dataset                        │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│          Stage 2: Data Validation (Anomaly Auditing)            │
│                   Outputs: Anomaly Reports                      │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│          Stage 3: Group Identifier (Louvain Cohort Grouping)    │
│                   Outputs: Cohort Group JSONs                   │
└─────────────────────────────────────────────────────────────────┘
                               ↓
┌─────────────────────────────────────────────────────────────────┐
│          Stage 4: Knowledge Insight (Sandboxed Query Engine)    │
│                   Outputs: Analytical Insights                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Key Design Principles

1. **Single Responsibility**: Each sub-agent focuses on a single task.
2. **Clear I/O Interfaces**: Pre-defined paths in `config.json` keep directories clean and isolated.
3. **Execution Sandboxing**: Analytical code generated by Stage 4 is checked and executed in a restricted context to prevent malicious operations.
4. **Composability**: Sub-agents can be run in part or in full, depending on what the Orchestrator needs.

---

## Configuration

Sub-agents read parameters under `LLM_MODULES` in `config.json`. These parameters configure fallback model names, temperatures, maximum retries, and output paths.

---

## Development

To implement a new pipeline stage or update an existing one:
1. Ensure new tools are added in the agent's `tools.py` module.
2. Document tools and datasets inside the agent's folder structure.
3. Register the new agent's runner inside `agents/sub_agents/__init__.py`.

---

## License

See LICENSE in the project root.