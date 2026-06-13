# Knowledge Insight Agent – Stage 4

The `knowledge_insight` agent is the **analytical query and insight agent** of the Agentic Tracking System. It generates Python analysis scripts (as a string) based on natural-language user queries, delegates execution to one of the sandboxed Insighter tools, and returns the computed analytical results.

The agent does **not** execute python code locally on the server, does **not** write to files, and does **not** modify datasets. All analysis is executed within a secure, isolated sandbox environment.

---

## Table of Contents

- [Overview](#overview)  
- [Agent Scope](#agent-scope)  
- [Tools](#tools)  
- [Executor Package](#executor-package)  
- [Execution Policy](#execution-policy)  
- [Recommended Models](#recommended-models)  
- [Installation](#installation)  
- [License](#license)

---

## Overview

The Knowledge Insight agent enables natural-language reasoning over attendance metrics, student communities, and security alerts. By writing specialized scripts to execute in an isolated runtime namespace, it handles complex correlations (e.g., comparing group attendance rates to security anomaly counts) without compromising system security.

---

## Agent Scope

- **Role**: Stage-4 read-only analytical insight generation.
- **Input**: Preprocessed sessions JSON, group memberships JSON, and CSV anomaly logs.
- **Forbidden**: Ingesting raw logs, altering database records, or returning source code blocks to the Orchestrator.
- **Output**: A single string result containing the computed answer.

---

## Tools

### `data_insighter_tool`
- Used for **attendance and cross-dataset analysis**.
- Preloads `attendance_data`, `groups_data`, and all alert tables (`identity_alerts`, `timestamp_alerts`, `device_alerts`).
- **Primary Tool** for correlations and multi-dataset evaluations.

### `groups_insighter_tool`
- Used for **group-only analysis**.
- Preloads only the `groups_data` mapping.

### `alerts_insighter_tool`
- Used for **security anomalies analysis**.
- Preloads the three alert tables: `identity_alerts`, `timestamp_alerts`, and `device_alerts`.

---

## Executor Package

The **executor** provides a secure, sandboxed execution engine used by all Insighter tools. It parses the generated Python code into an Abstract Syntax Tree (AST) to validate instructions before execution:

| File | Responsibility |
| :--- | :--- |
| `executor.py` | Implements `CodeExecutor` to compile, validate, and execute python scripts, returning standard strings. |
| `validator.py` | Implements `CodeValidator` to block unsafe imports (`os`, `sys`, etc.), dangerous functions, and dunder attributes. |
| `namespace.py` | Restricts the execution namespace to preloaded variables and safe math/json builtins. |
| `defaults.py` | Configures system timeouts, maximum steps, memory parameters, and forbidden keywords. |
| `exceptions.py` | Contains customized AST validation and runtime failure exceptions. |

---

## Execution Policy

- **Code Generation**: The agent writes python code as a string template and passes it to the selected tool; it **never executes code locally**.
- **Tool Selection**:
  * Attendance metrics or multi-dataset queries → `data_insighter_tool`
  * Cohort membership queries → `groups_insighter_tool`
  * Anomaly auditing queries → `alerts_insighter_tool`
- **Output Contract**: The final result must be assigned to the `result` string variable. The string must contain a one-line explanation and the answer.
- **Access Safety**: The script should use safe dictionary accesses (`get()`, `next(..., None)`) to prevent runtime crashes when matching records.

---

## Recommended Models

The agent utilizes models hosted on the **RAGaRenn** platform, selected in the following preference order:

| Model | Rating | Notes |
| :--- | :--- | :--- |
| **`analyse-de-risques`** | ⭐⭐⭐ | Optimal choice for individual anomaly modeling and risk metrics. |
| **`RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic`** | ⭐⭐ | Stable reasoning capability, excellent for generating clean, syntax-compliant Python snippets. |
| **`analyse-swot`** | ⭐ | Fallback model suited for basic descriptive analytics. |

---

## Installation

To install the agent package:

```bash
cd agents/sub_agents/knowledge_insight
pip install -e .
```

---

## License

See LICENSE in the project root.