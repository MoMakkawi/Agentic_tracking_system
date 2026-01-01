# Utils Package

## Index
- [Overview](#overview)
- [Features](#features)
  - [Helper Utilities](#helper-utilities)
  - [Data Models](#data-models)
  - [Storage Management](#storage-management)
  - [Configuration & Logging](#configuration--logging)
- [Usage](#usage)
  - [Basic Imports](#basic-imports)
  - [Example: Time Utilities](#example-time-utilities)
  - [Example: Configuration Management](#example-configuration-management)
  - [Example: Logging](#example-logging)
- [Project Structure](#project-structure)
- [Related Resources](#related-resources)

## Overview

**utils** is a core component of the **Agentic Tracking System**, providing robust utilities for multi-agent systems, intelligent tracking, and advanced data management in AI-driven applications.

## Features

### **Helper Utilities**
- **General Purpose Helpers** (`general.py`): Common utility functions for data manipulation and processing
- **Time-related Helpers** (`time.py`): Date, time handling, and temporal utilities for scheduling and tracking

### **Data Models**
- **Gemini Models** (`gemini.py`): Integration with Google Gemini models for LLM-powered functionality
- **RAGrenn Models** (`ragrenn.py`): Integration with RAGrenn models for LLM-powered functionality

### **Storage Management**
Abstraction layer for efficient data persistence and schema management:
- Database schema information retrieval
- Data persistence operations
- Storage optimization utilities

### **Configuration & Logging**
- **Config Module** (`config.py`): Centralized configuration management for the entire package
- **Logger Module** (`logger.py`): Structured logging utilities for debugging and monitoring
- **Secrets Management** (`Secrets.py`): Secure handling of API keys and sensitive credentials

## Usage

### Basic Imports

```python
from utils.helpers import general, time
from utils.models import gemini, ragrenn
from utils.storage import get_schema_info
from utils.config import load_config
from utils.logger import get_logger
```

### Example: Time Utilities

```python
from utils.helpers import time

# Handle temporal operations
timestamp = time.get_current_timestamp()
```

### Example: Configuration Management

```python
from utils.config import load_config, get_config

load_config()
config = get_config()
logs_url = config.SOURCE_URLS.LOGS
```

### Example: Logging

```python
from utils import logger

logger.info("Message")
```

## Project Structure

```
utils/
├── src/utils/
│   ├── helpers/
│   │   ├── general.py      # General-purpose utilities
│   │   └── time.py         # Time and date utilities
│   ├── models/
│   │   ├── gemini.py       # Gemini model integration
│   │   └── ragrenn.py      # Ragrenn model integration
│   ├── storage/            # Storage abstraction layer
│   ├── config.py           # Configuration management
│   ├── logger.py           # Logging configuration
│   └── Secrets.py          # Credentials and secrets
├── pyproject.toml          # Project metadata and dependencies
└── README.md              # This file
```

## Related Resources

- [Project Repository](https://github.com/MoMakkawi/Agentic_tracking_system)
- [Main Documentation](https://github.com/MoMakkawi/Agentic_tracking_system#readme)
