# Agentic Tracking System - Utils Package

## Index
- [Overview](#Overview)
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

---

## Overview

The **Utils Package** is the foundational library for the **Agentic Tracking System**, abstracting complex low-level operations into clean, reusable interfaces. It provides essential services such as configuration management with auto-reloading, a unified storage repository pattern, structured logging, and robust data transfer objects (DTOs).

Designed for multi-agent architectures, this package ensures consistency across data access, error handling, and external service integration (Google Gemini, RAGrenn).

---

## Installation

To install the package in your local environment, run the following command from the `utils` directory:

```bash
pip install .
```

Or if you are managing dependencies with Hatch/Poetry:

```bash
hatch shell
```

---

## Project Structure

The package is organized efficiently to separate concerns between data, logic, and infrastructure:

```text
src/utils/
├── config.py           # Centralized threaded configuration manager
├── logger.py           # Structured logging setup
├── Secrets.py          # Secure credentials handling
├── DTOs/               # Data Transfer Objects (Pydantic-style models)
│   ├── alerts/
│   ├── attendance/
│   └── groups/
├── mappers/            # Domain <-> DTO transformation logic
│   ├── alert_mappers.py
│   ├── group_mappers.py
│   └── session_mappers.py
├── storage/            # Repository Pattern Implementation
│   ├── base.py         # Abstract Base Class
│   ├── factory.py      # Repository Factory
│   ├── csv_repo.py     # CSV Storage
│   ├── json_repo.py    # JSON Storage
│   ├── jsonl_repo.py   # JSONL Storage
│   └── ics_repo.py     # iCalendar Storage
├── helpers/            # Utility functions
│   ├── general.py
│   └── time.py
└── models/             # AI Integration
    ├── gemini.py
    └── ragrenn.py
```

---

## Key Features

### Storage Layer
A robust **Repository Pattern** implementation that abstracts file I/O. It supports multiple backends (`.json`, `.jsonl`, `.csv`, `.ics`) through a unified interface (`RepositoryFactory`).
*   **Automatic type detection** based on file extension.
*   **CRUD operations**: `read_all`, `add`, `update`, `delete`.
*   **Object-Style Support**: `read`, `save`, and `update_dict` for managing settings or state files.
*   **Event Monitoring**: `IcsRepository.get_ending_events` for finding events ending within a specific time window.
*   **Schema introspection**: `get_schema_info`.

### Configuration Management
A thread-safe configuration manager that supports:
*   **Hot-reloading**: Automatically detects changes to `config.json` and updates the application state in real-time.
*   **Environment variable overrides**: Seamlessly inject secrets or environment-specific settings.
*   **Dot-notation access**: Access deeply nested config keys easily (e.g., `config.SOURCE_URLS.LOGS`).

### Data Transfer Objects (DTOs)
Strictly typed data structures for core domain entities:
*   **Attendance**: Tracking student presence.
*   **Groups**: Managing agent or student groupings.
*   **Alerts**: System notifications and anomalies.

### AI Models
Pre-configured wrappers for:
*   **Google Gemini**: For generative AI tasks.
*   **RAGrenn**: Custom RAG (Retrieval-Augmented Generation) implementation.

---

## Usage Examples

### Using the Storage Repositories

The `RepositoryFactory` automatically selects the correct driver for your file type.

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

Load the configuration once at startup. The watcher thread handles updates automatically.

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

Use the pre-configured logger for consistent output formats.

```python
from utils import logger

try:
    # Business logic here
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

See LICENSE in project root