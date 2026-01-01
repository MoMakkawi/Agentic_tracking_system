# Data Pipeline Agent – Stage-1 
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
`data_pipeline` is the **first-stage agent** of the Agentic Tracking System.  
It **ingests raw attendance logs & calendars**, cleans them, and returns a single pre-processed dataset—nothing more.

## Agent Scope
- **Role**: Stage-1 data ingestion & cleaning only.  
- **Forbidden**: validation, clustering, insight, retries, wrappers, conditionals.  
- **Output**: one plain confirmation sentence after successful run.

## Tools

### fetch_tool
- Downloads `.ics` + `.logs` from configured source (URL, path, DB).  
- Returns `{"logs":"&lt;path&gt;","ics":"&lt;path&gt;"}` or raises.

### preprocess_tool
- Cleans, timestamps, de-duplicates, standardizes records.  
- Returns `&lt;clean_dataset_path&gt;` or raises.

## Workflow
1. `fetch_tool()`  → acquire raw data  
2. `preprocess_tool()` → produce clean dataset  

Executed **exactly** in this order; any failure **halts immediately**.

## Hard Rules
- Emit **only** the mandatory 4-line block:
  ```python
  fetched_file_paths = fetch_tool()
  print(fetched_file_paths)

  clean_data_path = preprocess_tool()
  print(clean_data_path)
  ```
- No extra logic, loops, logs, or exposed paths.  
- Agent answer with one sentence like: “Fetch and preprocess completed.”

## Recommended Models (Ragarenn)
| Model | Stars | Notes |
|-------|-------|-------|
| `codestral:latest` | ⭐⭐⭐ | Built for pipelines, tools, deterministic execution |
| `mistralai/Mistral-Small-3.2-24B-Instruct` | ⭐⭐ | Solid instruction following + tool usage |
| `RedHatAI/Llama-3.3-70B-Instruct` | ⭐ | Use only if pipeline logic grows complex |

## Installation
```console
pip install data_pipeline
```

## License
MIT © 2026 Agentic Tracking System