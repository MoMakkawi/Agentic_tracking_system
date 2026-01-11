# Knowledge Insight Agent – Stage 4
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

It **generates Python analysis code** (as a string) based on user queries, delegates execution to the appropriate Insighter tool, and returns only the computed analytical result.

The agent does not execute code locally, **does not fetch, preprocess, validate, or modify data, and does not access external resources**. All execution is handled by sandboxed tools.

---

## Agent Scope
- **Role**: Generate analytical insights from existing, preloaded datasets only.   
- **Input**: 
  - Preprocessed attendance/session datasets
  - Group membership datasets
  - Security alert datasets (identity, timestamp, device)
- **Output**: 
  - A single string result assigned to result
  - No code, file paths, dataset dumps, or intermediate variables in the output

Intermediate variables may exist inside generated code, but must not appear in the final result string.

---

## Tools

### data_insighter_tool
- Primary entry point for **attendance and cross-domain analysis.**
- Loads preprocessed attendance data and identity alerts. 
- Provides access to:
  - `attendance_data`
  - `groups_data` (if needed for cross-domain analysis)
  - `identity_alerts`, `timestamp_alerts`, `device_alerts` (read-only).

Recommended tool for multi-dataset analysis

<details>
<summary>DataInsighter</summary>

**Workflow**:

```text
__init__:
  - Load attendance_data JSON
  - Initialize executor environment with datasets and helpers
```
*Entry point*: `DataInsighter.init() → ready-to-analyze environment`
</details>

### groups_insighter_tool
- Loads saved groups.  
- Exposes `groups_data` to **CodeExecutor** for interactive analysis.

<details>
<summary>GroupInsighter</summary>

**Workflow**:

```text
__init__:
  - Load groups
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

**Purpose**: Execute generated Python snippets against preloaded, read-only datasets with:
- AST-based validation
- Restricted imports
- Controlled execution time and memory

**Main Components**:

| File | Responsibility |
|------|----------------|
| `executor.py` | Implements **CodeExecutor** to validate and execute Python code, returning results |
| `validator.py` | **CodeValidator** parses AST to block unsafe imports, dangerous functions, and dunder attributes |
| `namespace.py` | Builds a restricted execution namespace from datasets and helper functions |
| `defaults.py` | Defines default modules, execution timeouts, and safety limits |
| `exceptions.py` | Custom exceptions for validation or runtime errors |

---

## Execution Policy

- The agent **generates Python code as a string**; it **never executes code directly** becuse Code execution is **delegated exclusively** to Insighter tools. 
- Tool selection depends on the focus of the question:  
  - Attendance or cross-domain analysis → `data_insighter_tool`  
  - Groups-only analysis → `groups_insighter_tool`  
  - Alerts-only analysis → `alerts_insighter_tool`  
- **Output Rules**: The final answer must be assigned to `result` variable. `result` must always be a string. Include one concise explanatory sentence in result. Do not return code, intermediate variables, or internal implementation details.  
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