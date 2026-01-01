# Data Validation Agent – Stage-2  
------------------------------------------------

## Table of Contents
- [Overview](#overview)  
- [Agent Scope](#agent-scope)  
- [Tools](#tools)  
- [Workflow](#workflow)  
- [Hard Rules](#hard-rules)  
- [Recommended Models (Ragarenn)](#recommended-models-ragarenn)  
- [Installation](#installation)  
- [License](#license)

## Overview
`DATA_VALIDATION` is the **second-stage agent** of the Agentic Tracking System.  
It **validates preprocessed attendance sessions**, runs **three anomaly-focused checks** (device, timestamp, identity), and **reports where the anomaly reports were saved—nothing else**.

## Agent Scope
- **Role**: Stage-2 anomaly validation only.  
- **Input**: preprocessed session dataset.  
- **Forbidden**: clustering, grouping, insights.  
- **Output**: one fixed final confirmation message.

## Tools

### device_validation_tool
- Internally uses the **DeviceValidator** class (see details below).  
- Returns `<device_anomaly_report_path>` or raises.

<details>
<summary>DeviceValidator internals (click to expand)</summary>

The **DeviceValidator** analyzes device-level behavior across sessions and produces device–session anomaly alerts.

| Step | What it does |
|------|--------------|
| **Load** | Read preprocessed session JSON |
| **Flatten** | Build per-log DataFrame with `session_id`, `device_id`, timestamps |
| **Detect missing data** | Flag missing `device_id`, `session_id`, or `received_at` |
| **Detect clock resets** | Flag date mismatches between log date and received date |
| **Detect long sessions** | Flag device–session durations exceeding configured hours |
| **Collect alerts** | Aggregate issues per device–session |
| **Save** | Persist alerts to CSV |

Entry point: `DeviceValidator.run()` → alerts, then `save()` → CSV path.
</details>

---

### timestamp_validation_tool
- Internally uses the **TimestampValidator** class (see details below).  
- Returns `<timestamp_anomaly_report_path>` or raises.

<details>
<summary>TimestampValidator internals (click to expand)</summary>

The **TimestampValidator** checks time-based correctness of check-ins.

| Step | What it does |
|------|--------------|
| **Load** | Read preprocessed session JSON |
| **Flatten** | Build timestamped table with `uid`, `timestamp`, `session_id`, `device_id` |
| **Validate dates** | Flag check-ins outside semester range |
| **Validate hours** | Flag check-ins outside daily allowed time window |
| **Detect invalid days** | Flag weekend and holiday check-ins |
| **Collect alerts** | Group reasons per UID–timestamp–session–device |
| **Save** | Persist alerts to CSV |

Entry point: `TimestampValidator.run()` then `save()` returns CSV path.
</details>

---

### identity_validation_tool
- Internally uses the **IdentityValidator** class (see details below).  
- Returns `<identity_anomaly_report_path>` or raises.

<details>
<summary>IdentityValidator internals (click to expand)</summary>

The **IdentityValidator** analyzes UID behavior across sessions and devices.

| Step | What it does |
|------|--------------|
| **Load** | Read preprocessed session JSON |
| **Flatten** | Build DataFrame with `uid`, `session_id`, `device_id`, `redundant_count` |
| **Flag patterns** | Detect UIDs not matching expected hex-like format |
| **Detect redundancy** | Flag highly redundant UIDs within sessions |
| **Detect rarity** | Flag globally rare or single-occurrence UIDs |
| **Track history** | Record per-UID anomaly sessions and repeat counts |
| **Collect alerts** | Build UID–device alert rows with reasons |
| **Save** | Persist alerts to CSV |

Entry point: `IdentityValidator.run()` → alerts, then `save()` → CSV path.
</details>

---

## Workflow
Executed **exactly** as follows; any failure **halts immediately**.

```python
device_report_path = device_validation_tool()
print("Device anomalies report path:", device_report_path)

timestamp_report_path = timestamp_validation_tool()
print("Timestamp anomalies report path:", timestamp_report_path)

identity_report_path = identity_validation_tool()
print("Identity anomalies report path:", identity_report_path)

final_answer("Device & Timestamp & Identity Validations complete.")
```

## Hard Rules
- The agent is authorized to execute **only** the following tools:
  - `device_validation_tool()`
  - `timestamp_validation_tool()`
  - `identity_validation_tool()`
- Unless explicitly restricted by the task, **all three tools must be executed**.
- Each tool’s returned value **will be printed** using the exact descriptive prefixes defined in the workflow.
- The agent **must not fabricate** file paths or infer tool outputs.
- No additional logic is permitted, including loops, retries, conditionals, wrappers, or helper functions.
- The final agent response **must be exactly**:

Device & Timestamp & Identity Validations complete.

## Recommended Models (Ragarenn)
| Model | Stars | Notes |
|-------|-------|-------|
| `analyse-de-risques` | ⭐⭐⭐ | Optimal for anomaly detection and validation workflows |
| `RedHatAI/Llama-3.3-70B-Instruct` | ⭐⭐ | Reliable for structured reasoning and complex instruction handling |
| `mistralai/Mistral-Small-3.2-24B-Instruct` | ⭐ | Best suited for lightweight validation tasks |

## Installation
```console
pip install data_validation
```
## License
MIT © 2026 Agentic Tracking System