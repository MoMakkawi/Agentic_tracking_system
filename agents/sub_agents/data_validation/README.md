# Data Validation Agent – Stage 2

The `data_validation` agent is the **second-stage agent** of the Agentic Tracking System. It validates preprocessed attendance sessions, executes three specialized anomaly validation checks (device, timestamp, identity), and writes CSV anomaly reports.

---

## Table of Contents

- [Overview](#overview)
- [Agent Scope](#agent-scope)
- [Tools](#tools)
- [Workflow](#workflow)
- [Hard Rules](#hard-rules)
- [Recommended Models](#recommended-models)
- [Installation](#installation)
- [License](#license)

---

## Overview

Data validation ensures the integrity, compliance, and authenticity of badge logs. By running sequential validators, the system flags hardware misconfigurations, illegal check-in dates/times, and redundant or suspicious identity scans before cohort grouping.

---

## Agent Scope

- **Role**: Stage-2 anomaly validation.
- **Input**: Preprocessed session data.
- **Forbidden**: Cohort clustering, query answering, and data modification.
- **Output**: Reports paths to generated validation logs.

---

## Tools

### `device_validation_tool`
- Scans preprocessed sessions to detect device-level errors (missing identifiers, long durations, and clock resets).
- Internally wraps the `DeviceValidator` logic.
- **Returns**: The path to the device anomalies CSV report.

### `timestamp_validation_tool`
- Verifies check-in timestamps against semester dates, daily operating hours, and holiday schedules.
- Internally wraps the `TimestampValidator` logic.
- **Returns**: The path to the timestamp anomalies CSV report.

### `identity_validation_tool`
- Audits student check-in IDs for structural hex patterns, redundancy spikes, and global check-in rarity.
- Internally wraps the `IdentityValidator` logic.
- **Returns**: The path to the identity anomalies CSV report.

---

## Workflow

The agent executes the validation check tools in an **immutable** sequence:

```python
device_report_path = device_validation_tool()
print("Device anomalies report path:", device_report_path)

timestamp_report_path = timestamp_validation_tool()
print("Timestamp anomalies report path:", timestamp_report_path)

identity_report_path = identity_validation_tool()
print("Identity anomalies report path:", identity_report_path)

final_answer("Validation complete. Do you want to categorize attendees into groups?")
```

---

## Hard Rules

- **Execution Compliance**: Unless explicitly instructed to process a subset, the agent must run **all three tools** in the exact order: `device_validation_tool` → `timestamp_validation_tool` → `identity_validation_tool`.
- **Formatting Constraints**: The output files must be printed using the exact console prefixes (`Device anomalies report path:`, etc.) defined in the workflow.
- **Safety Policy**: The agent must not fabricate file paths or inject custom verification logic (no loops, conditionals, or wrappers are allowed).

---

## Recommended Models

The agent utilizes models hosted on the **RAGaRenn** platform, selected in the following preference order:

| Model | Rating | Notes |
| :--- | :--- | :--- |
| **`RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic`** | ⭐⭐⭐ | Strong structured reasoning, excellent tool parameter control, and compliance with immutable sequences. |
| **`analyse-de-risques`** | ⭐⭐ | Tailored for risk categorization and security auditing checks. |
| **`mistralai/Mistral-Small-3.2-24B-Instruct-2506`** | ⭐ | Fast, lightweight instruction-following model for basic validation workflows. |

---

## Installation

To install the agent package:

```bash
cd agents/sub_agents/data_validation
pip install -e .
```

---

## License

See LICENSE in the project root.