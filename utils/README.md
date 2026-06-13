# Agentic Tracking System - Utils Package

The **Utils Package** is the foundational shared library for the Agentic Tracking System, abstracting complex low-level operations into clean, reusable interfaces. It provides essential services such as configuration management with hot-reloading, a unified storage repository pattern, DTO (Data Transfer Object) mapping, structured logging, and helpers for timezone operations.

Designed specifically for multi-agent architectures, this package ensures data consistency, error handling, and external model integrations (Google Gemini, RAGaRenn) across the system.

---

## Index

- [Overview](#overview)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Key Features](#key-features)
  - [Storage Layer](#storage-layer)
  - [Configuration Management](#configuration-management)
  - [Data Transfer Objects (DTOs)](#data-transfer-objects-dtos)
  - [AI Models](#ai-models)
- [Usage Examples](#usage-examples)
  - [Using the Storage Repositories](#using-the-storage-repositories)
  - [Managing Configuration](#managing-configuration)
  - [Structured Logging](#structured-logging)
  - [Time Utilities](#time-utilities)
- [License](#license)

---

## Overview

The `utils` package ensures that both the API backend and the orchestrated AI Agents read from the same configuration, interact with the same storage schemas, and log in a standardized format. 

---

## Installation

To install the package in your local environment, run the following command from the `utils` directory:

```bash
pip install -e .
```

---

## Project Structure

The package is organized to separate concerns between data mapping, storage adapters, helpers, and AI models:

```text
src/utils/
├── config.py           # Thread-safe configuration manager with file watcher
├── logger.py           # Structured logging utility
├── Secrets.py          # Secure environment variables helper
├── DTOs/               # Data Transfer Objects (Pydantic-style models)
│   ├── alerts/         # Validation alerts (device, identity, timestamp)
│   ├── attendance/     # Sessions and attendance logs
│   └── groups/         # Student cohort structures
├── mappers/            # Domain model <-> DTO transformation logic
│   ├── alert_mappers.py
│   ├── group_mappers.py
│   └── session_mappers.py
├── storage/            # Repository Pattern implementation
│   ├── base.py         # Abstract Base Class
│   ├── factory.py      # Repository Factory
│   ├── csv_repo.py     # CSV Storage adapter
│   ├── json_repo.py    # JSON Storage adapter
│   ├── jsonl_repo.py   # JSONL Storage adapter
│   └── ics_repo.py     # iCalendar (ICS) Storage adapter
├── helpers/            # Helper utilities
│   ├── general.py
│   └── time.py         # Timezone conversion and checking helpers
└── models/             # AI model integration layer
    ├── gemini.py       # Google Gemini model wrapper
    └── Ragarenn.py     # RAGaRenn client wrapper
```

---

## Key Features

### Storage Layer
A robust **Repository Pattern** implementation that abstracts file I/O operations. It supports multiple backends (`.json`, `.jsonl`, `.csv`, `.ics`) through a unified factory interface (`RepositoryFactory`).
* **Automatic Type Detection**: Selects the appropriate repository driver based on the file extension.
* **CRUD Operations**: Standardized methods (`read_all`, `add`, `update`, `delete`).
* **Settings & State Management**: Supports `read` and `save` for managing configurations or runtime states.
* **iCalendar Event Monitoring**: `IcsRepository.get_ending_events` retrieves events ending within a specific time window, supporting scheduler triggers.
* **Schema Introspection**: `get_schema_info` returns structural schema layouts for downstream AI agents.

### Configuration Management
A thread-safe configuration manager featuring:
* **Hot-Reloading**: A background watcher thread automatically detects updates in `config.json` and updates the runtime configuration state without requiring a service restart.
* **Environment Variable Overrides**: Securely injects credentials and secrets.
* **Dot-Notation Access**: Access nested settings intuitively (e.g., `config.SOURCE_URLS.LOGS`).

### Data Transfer Objects (DTOs)
Strictly typed data structures using Pydantic schemas for core system domains:
* **Attendance**: Managing raw scans and structured attendance sessions.
* **Groups**: Maintaining cohort clusters.
* **Alerts**: Encapsulating anomaly classifications (device, identity, timestamp).

### AI Models
Unified model wrappers that present a clean interface to `smolagents`:
* **Google Gemini**: Integrates Gemini generative AI capabilities.
* **RAGaRenn**: A client wrapper for the RAGaRenn open-source generative AI platform.

---

## Usage Examples

### Using the Storage Repositories

The `RepositoryFactory` automatically selects the correct driver for your file type:

```python
from utils import RepositoryFactory

# Initialize repository (Auto-detects JSON driver)
user_repo = RepositoryFactory.get_repository("data/users.json")

# Create
user_repo.add({"id": "1", "name": "Alice", "role": "admin"})

# Read
all_users = user_repo.read_all()
print(f"Total users: {len(all_users)}")

# Update
user_repo.update("1", {"name": "Alice Smith"})

# Delete
user_repo.delete("1")
```

### Managing Configuration

Load the configuration once at startup. The watcher thread handles updates automatically:

```python
from utils import load_config, get_config

# Initialize with auto-reload enabled
load_config("config.json", start_watcher=True)

# Access configuration anywhere in your app
config = get_config()

# Access nested keys using dot notation
log_level = config.LOGGING.LEVEL
api_key = config.API_KEYS.GEMINI

print(f"System running with log level: {log_level}")
```

### Structured Logging

Use the pre-configured logger for consistent output formats:

```python
from utils import logger

try:
    logger.info("Processing started...")
except Exception as e:
    logger.error(f"Processing failed: {e}")
```

### Time Utilities

```python
from utils import TimestampHelper

# Get standardized Paris time
current_ts = TimestampHelper.now_paris()
print(f"Action recorded at: {current_ts}")

# Check if a time is within a ±30s window of now
is_now = TimestampHelper.is_within_window(current_ts)
```

---

## License

See LICENSE in the project root.