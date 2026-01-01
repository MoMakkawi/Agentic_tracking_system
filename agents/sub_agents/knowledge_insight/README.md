# Knowledge Insight Agent – Analytical Stage
------------------------------------------------

## Table of Contents
- [Overview](#overview)  
- [Agent Scope](#agent-scope)  
- [Tools](#tools)  
- [Executor Package](#executor-package)  
- [Execution Policy](#execution-policy)  
- [Recommended Models (Ragarenn)](#recommended-models-ragarenn)  
- [Installation](#installation)  
- [License](#license)

---

## Overview
`knowledge_insight` is the **analytical insight agent** of the Agentic Tracking System.  
It **generates Python analysis code** for attendance sessions, group memberships, and alerts, sends it to the proper execution tool, and returns only the computed result.  

It **does not fetch, preprocess, validate, or modify data**; it only analyzes in-memory datasets.

---

## Agent Scope
- **Role**: Analytical insights from existing datasets only.  
- **Forbidden**: data fetching, preprocessing, validation, persistence, or reporting.  
- **Output**: a single computed result assigned to `result`; no code, paths, or intermediate variables.

---

## Tools

### data_insighter_tool
- Loads preprocessed attendance data and identity alerts.  
- Exposes datasets and helpers (like `is_valid_id`) to **CodeExecutor** for analysis.

<details>
<summary>DataInsighter</summary>

**Workflow**:

```text
__init__:
  - Load attendance_data JSON
  - Load identity alerts CSV, compute invalid UIDs, create is_valid_id helper
  - Initialize executor environment with datasets and helpers
```
*Entry point*: `DataInsighter.init() → ready-to-analyze environment`

</details>

### groups_insighter_tool
- Loads saved student groups JSON from `PATHS.GROUPS`.  
- Exposes `"groups_data"` to **CodeExecutor** for interactive analysis.

<details>
<summary>GroupInsighter</summary>

**Workflow**:

```text
__init__:
  - Load groups JSON into memory
  - Populate datasets dictionary with "groups_data"
  - Initialize executor environment
```
*Entry point*: `GroupInsighter.init() → ready-to-analyze environment`

</details>

### alerts_insighter_tool
- Loads identity, timestamp, and device alert CSVs.  
- Exposes all three alert datasets to **CodeExecutor** for interactive analysis.

<details>
<summary>AlertsInsighter</summary>

**Workflow**:

```text
__init__:
  - Load CSV files into memory
  - Build datasets dictionary with three alert tables
  - Initialize executor environment
```
*Entry point*: `AlertsInsighter.init() → ready-to-analyze environment`

</details>

## Executor Package

The **executor** provides a secure, sandboxed Python execution engine used by all Insighter tools.

**Purpose**: Run Python snippets against in-memory datasets (attendance, groups, alerts) with strict validation, restricted imports, and controlled execution.

**Main Components**:

| File | Responsibility |
|------|----------------|
| `executor.py` | Implements **CodeExecutor** to validate and execute Python code, returning results |
| `namespace.py` | Builds a restricted execution namespace from datasets and helper functions |
| `defaults.py` | Defines default modules, execution timeouts, and safety limits |
| `exceptions.py` | Custom exceptions for validation or runtime errors |
| `validator.py` | **CodeValidator** parses AST to block unsafe imports, dangerous functions, and dunder attributes |

---

## Execution Policy

- The agent **generates Python code only**; it **never executes code directly**.  
- Tool selection depends on the focus of the question:  
  - Attendance/session questions → `data_insighter_tool`  
  - Group questions → `groups_insighter_tool`  
  - Alerts questions → `alerts_insighter_tool`  
- **Output**: Only the final computed insight assigned to `result`.  
- Do **not** return code, intermediate variables, or internal implementation details.  
- Requests outside attendance, groups, or alerts are rejected with a fixed clarification message.

---

## Recommended Models (Ragarenn)

| Model | Stars | Notes |
|-------|-------|-------|
| `analyse-de-risques` | ⭐⭐⭐ | Individual anomaly & risk modeling |
| `RedHatAI/Llama-3.3-70B-Instruct` | ⭐⭐ | Strong behavioral reasoning |
| `mistralai/Mistral-Small-3.2-24B-Instruct` | ⭐ | Suitable for simpler analysis tasks |

---

## Installation
```console
pip install knowledge_insight
```

## License
MIT © 2026 Agentic Tracking System