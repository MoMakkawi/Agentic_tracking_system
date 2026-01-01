# Data Pipeline Agent – Stage 1 
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
- Downloads `.ics` + `.logs` from configured source (URLs) and store them in the configured paths, internally uses the `DataFetcher` class (see details below).
- Returns `{"logs":"<path>","ics":"<path>"}` or raises.

<details>
<summary>DataFetcher internals (click to expand)</summary>

The **DataFetcher** class handles the actual download and persistence.

| Step | What it does |
|------|--------------|
| **Validate** | Check that all required URLs & target paths are present |
| **Download** | Fetch JSONL logs & ICS calendars with timeout / retry logic |
| **Store** | Write bytes to disk via `RepositoryFactory` (JSONL → logs, ICS → calendar) |
| **Return** | `{"logs":"<path>","ics":"<path>"}` on success, raises on any failure |

Entry point: `DataFetcher.run()` executes download + save and returns the path dict.
</details>

### preprocess_tool
- Internally uses the `Preprocessor` class (see details below).  
- Returns `<clean_dataset_path>` or raises.

<details>
<summary>Preprocessor internals (click to expand)</summary>

The **Preprocessor** loads raw attendance logs & ICS calendars, cleans and deduplicates scans, builds session objects, enriches them with overlapping calendar events, and writes the final structured dataset to JSON.

| Step | What it does |
|------|--------------|
| **Load** | Read JSONL logs + ICS events from configured paths |
| **Clean** | Drop redundant badge scans per UID, store redundancy stats |
| **Sessionise** | Aggregate logs into sessions (counts, timestamps, metadata) |
| **Enrich** | Match each session with overlapping ICS event(s) and attach titles |
| **Save** | Persist enriched sessions to a JSON file for downstream agents |

Entry point: `Preprocessor.run()` executes the full chain and returns the output path.
</details>

Executed **exactly** in this order; any failure **halts immediately**.

## Hard Rules
- Emit **only** the mandatory 4-line block:
  ```python
  fetched_file_paths = fetch_tool()
  print(fetched_file_paths)

  clean_data_path = preprocess_tool()
  print(clean_data_path)

  final_answer("Fetch and preprocess completed.")
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