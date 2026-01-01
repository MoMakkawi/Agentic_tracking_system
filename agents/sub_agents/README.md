# Sub Agents Package

## Overview

The **sub_agents** package contains four specialized agent modules that form the **multi-stage pipeline** of the Agentic Tracking System. Each agent operates independently but passes refined data to the next stage, creating a deterministic, composable workflow for attendance tracking and analysis.

## Architecture

The system follows a **sequential 4-stage architecture**:

```
Source URLs → [Stage 1] → [Stage 2] → [Stage 3] → [Stage 4] → Insights
```

Each stage has:
- **Single responsibility**: One task, no cross-cutting concerns
- **Clear input/output contract**: Defined data formats
- **Tool-based automation**: Specific agent tools for each stage

---

## Agents

### 1. Data Pipeline Agent – Stage 1
**Module**: `data_pipeline`

**Purpose**: Raw data fetching and cleaning

**Responsibilities**:
- Downloads `.ics` calendar files and `jsonl` attendance logs from configured sources
- Parses and validates file formats
- Cleans and standardizes raw data
- Outputs a single pre-processed dataset

**Key Constraint**: No validation, no clustering—purely data extraction and cleaning

**Tools**:
- `fetch_tool`: Download files from URLs
- `preprocess_tool`: Clean and standardize data

**Output**: Pre-processed attendance data in standard format

**Documentation**: See [`data_pipeline/README.md`](./data_pipeline/README.md)

---

### 2. Data Validation Agent – Stage 2
**Module**: `data_validation`

**Purpose**: Data quality assurance and validation

**Responsibilities**:
- Validates data integrity and completeness
- Checks for missing values, duplicates, and anomalies
- Applies consistency rules across datasets
- Flags problematic records for review

**Key Constraint**: No clustering or grouping—validation only

**Output**: Alerts datasets

**Documentation**: See [`data_validation/README.md`](./data_validation/README.md)

---

### 3. Group Identifier Agent – Stage 3
**Module**: `group_identification`

**Purpose**: Attendance pattern clustering/group identification

**Responsibilities**:
- Analyzes attendance patterns across individuals
- Identifies behavioral groups/clusters

**Key Constraint**: No insights generation—clustering only

**Output**: Group assignments and behavior signatures

**Documentation**: See [`group_identification/README.md`](./group_identification/README.md)

---

### 4. Knowledge Insight Agent – Stage 4
**Module**: `knowledge_insight`

**Purpose**: Insight generation and actionable intelligence

**Responsibilities**:
- Analyzes sessions and groups and alerts data for patterns and trends
- Generates actionable insights and recommendations
- Provides strategic guidance for attendance management

**Key Constraint**: Works only with validated, grouped data from prior stages

**Output**: Insights, recommendations

**Documentation**: See [`knowledge_insight/README.md`](./knowledge_insight/README.md)

---

## Package Structure

```
sub_agents/
├── data_pipeline/              # Stage 1: Data ingestion & cleaning
│   ├── src/data_pipeline/      # Main implementation
│   ├── README.md               # Detailed documentation
│   ├── __init__.py
│   └── pyproject.toml
├── data_validation/            # Stage 2: Data quality validation
│   ├── src/data_validation/
│   ├── README.md
│   ├── __init__.py
│   └── pyproject.toml
├── group_identification/       # Stage 3: Pattern clustering
│   ├── src/group_identification/
│   ├── README.md
│   ├── __init__.py
│   └── pyproject.toml
├── knowledge_insight/          # Stage 4: Insight generation
│   ├── src/knowledge_insight/
│   ├── README.md
│   ├── __init__.py
│   └── pyproject.toml
└── __init__.py                 # Package entry point
```

## Installation

Install the entire sub-agents package:

```bash
cd agents/sub_agents
pip install -e .
```

Or install individual agents:

```bash
cd agents/sub_agents/data_pipeline
pip install -e .
```

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

Each agent is designed to be orchestrated by the parent Agent class:

```python
task1 = "Stage 1: Fetch and preprocess"
rawdata = data_pipeline_main(task1)

task2 = "Stage 2: Validate data"
validated_data = data_validation_main(task2)

task3 = "Stage 3: Identify groups"
groups = group_identification_main(task3)

task4 = "Stage 4: Generate insights"
insights = knowledge_insight_main(task4)
```

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                   Input: .ics & .logs URLs                      │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│          Stage 1: Data Pipeline (Ingestion & Cleaning)          │
│                   Outputs: Clean Dataset                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│     Stage 2: Data Validation (Quality & Consistency)            │
│                   Outputs: Alerts Dataset                       │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│    Stage 3: Group Identifier (Clustering & Patterns)            │
│                   Outputs: Groups                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│     Stage 4: Knowledge Insight (Insights & Intelligence)        │
│                   Outputs: Insights                             │
└─────────────────────────────────────────────────────────────────┘
```

## Key Design Principles

1. **Single Responsibility**: Each agent does one thing well
2. **Clear Contracts**: Defined input/output formats between stages
3. **Composability**: Agents can be tested and deployed independently
4. **Determinism**: No randomness, enabling reproducible results
5. **Tool-Based Execution**: Each agent uses specific tools for its domain
6. **No Cross-Cutting Concerns**: No validation in pipeline stage, no clustering in validation stage

## Configuration

Agent configuration is handled through:
- Environment variables
- Config files (`pyproject.toml`, `.env`)
- Runtime parameters passed from the orchestrator

See individual agent READMEs for configuration details.

## Development

To extend the sub-agents system:

1. **Create a new agent**: Follow the structure of existing agents
2. **Define tools**: Implement agent-specific tools
3. **Set input/output contracts**: Document expected data formats
4. **Update Configs**: Update configuration file
5. **Document thoroughly**: README explaining purpose and usage
6. **Integrate**: Register in the parent orchestrator


## Recommended LLM Models

For optimal agent performance, use these models:

- **`codestral:latest`**: Best for deterministic pipeline tasks
- **`mistralai/Mistral-Small-3.2-24B-Instruct`**: Good balance for all stages
- **`RedHatAI/Llama-3.3-70B-Instruct`**: For complex insight generation

Model selection depends on:
- Task complexity (pipeline < insight generation)
- Available compute resources
- Required reasoning depth

## Contributing

When modifying agents:
1. Maintain single responsibility principle
2. Update documentation
3. Add/update tests
4. Follow existing code style
5. Test the entire pipeline

## License

MIT © 2026 Agentic Tracking System

## See Also

- [Parent Agents Documentation](../README.md)
- [Individual Agent Documentation](./data_pipeline/README.md)
- [Project Main README](../../README.md)