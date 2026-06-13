# Data Pipeline Agent – Stage 1

The `data_pipeline` agent is the **first-stage agent** of the Agentic Tracking System. It ingests raw attendance logs and schedules, cleans them, structures them into sessions, and returns a single preprocessed dataset.

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

This agent is responsible for raw file extraction and standardization. It maps raw check-in records to calendar events defined in `.ics` schedules, deduplicates badge scans, and prepares a structured JSON file for downstream validation and cohort grouping.

---

## Agent Scope

- **Role**: Stage-1 data ingestion and preprocessing.
- **Input**: Configured URLs pointing to raw check-in logs and iCalendar schedules.
- **Forbidden**: Anomaly detection, validation auditing, cohort clustering, and analytical answering.
- **Output**: A confirmation message indicating successful preprocessing.

---

## Tools

### `fetch_tool`
- Downloads raw `.jsonl` check-in logs and `.ics` calendars from configured endpoints and persists them to configured target directories.
- Internally wraps the `DataFetcher` helper.
- **Returns**: A directory map (e.g., `{"logs": "<path>", "ics": "<path>"}`).

### `preprocess_tool`
- Deduplicates raw badge scans (tracking duplicate counts), structures scans into sessions, and matches sessions to overlapping scheduled events.
- Internally wraps the `Preprocessor` logic.
- **Returns**: The output filepath of the clean preprocessed dataset.

---

## Workflow

The agent executes the pipeline tools in an **immutable** sequence:

1. **Download Raw Data**: Call `fetch_tool()` to retrieve files.
2. **Standardize and Enrich**: Call `preprocess_tool()` to process and align logs with calendars.
3. **Notify Orchestrator**: Call `final_answer()` to return the pipeline status.

---

## Hard Rules

- **Code Block Execution**: The agent must output and execute **only** the following 4-line python block:
  ```python
  fetched_file_paths = fetch_tool()
  print(fetched_file_paths)

  clean_data_path = preprocess_tool()
  print(clean_data_path)

  final_answer("Data fetched and preprocessed successfully. Do you want to validate it?")
  ```
- **Constraints**: No conditionals, loops, retries, wrappers, helper functions, or additional reasoning steps are allowed.
- **Failure Policy**: Execution halts immediately on any tool failure or empty output.

---

## Recommended Models

The agent utilizes models hosted on the **RAGaRenn** platform, selected in the following preference order:

| Model | Rating | Notes |
| :--- | :--- | :--- |
| **`analyse-de-risques`** | ⭐⭐⭐ | Highly optimized for data extraction, schema mapping, and preprocessing logic. |
| **`openai/gpt-oss-120b`** | ⭐⭐ | Reliable reasoning capabilities for processing raw calendar dates and tables. |
| **`mistralai/Mistral-Small-3.2-24B-Instruct-2506`** | ⭐ | Lightweight, deterministic execution of code and tool parameters. |

---

## Installation

To install the agent package:

```bash
cd agents/sub_agents/data_pipeline
pip install -e .
```

---

## License

See LICENSE in the project root.