# Group Identifier Agent – Stage 3

The `group_identification` agent is the **third-stage agent** of the Agentic Tracking System. It clusters attendees into behavioral groups using a Louvain-based community detection algorithm and persists the groupings to storage, returning a confirmation message.

The agent does **not** perform exploratory data analysis, validation checks, reporting, or response explanations. Its responsibility ends immediately after groups are successfully saved.

---

## Table of Contents

- [Overview](#overview)  
- [Agent Scope](#agent-scope)  
- [Tools](#tools)  
- [Workflow](#workflow)  
- [Execution Policy & Hard Rules](#execution-policy--hard-rules)  
- [Recommended Models](#recommended-models)  
- [Installation](#installation)  
- [License](#license)

---

## Overview

Student grouping helps advisors analyze collective behaviors and identify low-engagement cohorts early. By modeling co-attendance as a weighted similarity graph, this agent runs community detection to partition students into distinct clusters.

---

## Agent Scope

- **Role**: Stage-3 cohort clustering and grouping.
- **Input**: Preprocessed sessions dataset and optional identity alerts.
- **Forbidden**: Query reasoning, anomaly validations, and code generation.
- **Output**: A single confirmation string indicating successful grouping.

---

## Tools

### `louvain_clustering_tool`
- Maps student check-in feature vectors (attendance frequency, average group size, and co-attendance patterns) into a weighted similarity graph.
- Applies Louvain community detection to detect student clusters.
- **Returns**: A dictionary mapping group names to list of participant UIDs (e.g., `{"Group 1": ["uid1", ...], ...}`).

### `save_tool`
- Persists the generated group dictionary to JSON in the configured storage path (`PATHS.GROUPS`).
- **Returns**: The storage file path where the JSON was saved.

---

## Workflow

The agent executes tools in the following **immutable** sequence:

```python
groups = louvain_clustering_tool()
print(groups)

groups_path = save_tool(groups)
print(groups_path)

final_answer("Groups saved successfully.")
```

---

## Execution Policy & Hard Rules

### 1. Default Execution (No Explicit Criteria)
If the Orchestrator does **not** specify custom grouping criteria, the agent must:
1. Run `louvain_clustering_tool()` to detect clusters.
2. Print the groups dictionary.
3. Save groups via `save_tool()`.
4. Print the saved storage path.
5. Return the exact final confirmation message: `"Groups saved successfully."`

> **Constraint**: Do not return raw dictionary content or file paths in the final text response.

### 2. User-Defined Grouping Criteria (Conditional)
If the Orchestrator passes concrete partitioning parameters:
- The agent may inspect `attendance_data` and `identity_alerts` schemas.
- It must ensure that:
  - Every UID belongs to exactly **one** group.
  - There are no duplicate UIDs across cohorts.
  - There are no unassigned UIDs.
- If criteria are vague, ambiguous, or incomplete, the agent **must ignore them** and fall back to the default Louvain clustering workflow.

---

## Recommended Models

The agent utilizes models hosted on the **RAGaRenn** platform, selected in the following preference order:

| Model | Rating | Notes |
| :--- | :--- | :--- |
| **`RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic`** | ⭐⭐⭐ | Best balance of deterministic logic and compliance with sequence restrictions. |
| **`openai/gpt-oss-120b`** | ⭐⭐ | Powerful reasoning model, suitable for complex parsing of conditional criteria. |
| **`mistralai/Mistral-Small-3.2-24B-Instruct-2506`** | ⭐ | Lightweight, fast model optimized for standard default executions. |

---

## Installation

To install the agent package:

```bash
cd agents/sub_agents/group_identification
pip install -e .
```

---

## License

See LICENSE in the project root.