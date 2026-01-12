# Agentic Tracking System

## Index

- [Executive Summary](#executive-summary)
- [System Architecture](#system-architecture)
- [Key Features](#key-features)
- [Component Overview](#component-overview)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Running the System](#running-the-system)
- [Configuration](#configuration)
- [Development](#development)
- [License](#license)

## Executive Summary

The **Agentic Tracking System** is a sophisticated, multi-agent platform designed to monitor, analyze, and manage complex workflows in real-time. It combines a high-performance **FastAPI** backend, a premium **React** dashboard, and an orchestrated fleet of **AI Agents** to provide intelligent insights and automated control.

Key capabilities include real-time attendance tracking, dynamic group analytics, automated system alerts, and a natural language interface for interacting with system data.

---

## System Architecture

The system follows a modular micro-services architecture, orchestrated by a central intelligent agent.

```mermaid
graph TD
    User[User] -->|Interacts| Dashboard[React Dashboard]
    Dashboard -->|HTTP/REST| API[FastAPI Backend]
    
    subgraph "Core System"
        API -->|Dispatches| Orchestrator[Orchestrator Agent]
        Orchestrator -->|Coordinates| SubAgents[Sub-Agents]
        
        SubAgents -->|Data Pipeline| Data Pipeline Agent
        SubAgents -->|Analyst| Knowledge Insights Agent
        SubAgents -->|Validator| Validation Agent
    end
    
    subgraph "Infrastructure"
        API -->|Reads/Writes| Utils[Shared Utils Library]
        Orchestrator -->|Uses| Utils
        Utils -->|Persists| Storage[(Data Storage)]
        Utils -->|Config| Config[Config Manager]
    end
```

---

## Key Features

-   **Orchestrated Agentic Workflows**
    A central Orchestrator agent intelligently routes tasks to specialized sub-agents (Data Pipeline, Validation, Analytics) to handle complex requests securely and efficiently.

-   **Cool Dashboard**
    A stunning, "Deep Ocean" themed interface built with React and Vite. Features glassmorphism effects, interactive charts, and a responsive layout for monitoring system health at a glance.

-   **Robust Data Pipeline**
    Automated ingestion, validation, and processing of data streams. Supports multiple data formats (JSON, CSV, ICS) with a unified repository pattern.

-   **Dynamic Configuration**
    Hot-reloadable configuration management allows for system tuning without downtime. Securely handles credentials and environment-specific settings.

---

## Component Overview

| Component | Directory | Description |
| :--- | :--- | :--- |
| **Dashboard** | [`/dashboard`](./dashboard/README.md) | The frontend user interface. Built with React, Vite, and Tailwind-inspired CSS. |
| **API** | [`/api`](./api/Readme.md) | The RESTful backend service. Built with FastAPI, handling client requests and agent dispatch. |
| **Agents** | [`/agents`](./agents/orchestrator/README.md) | The intelligence layer. Contains the Orchestrator and specialized sub-agents. |
| **Utils** | [`/utils`](./utils/README.md) | The shared core library. Handles storage, logging, configuration, and common models. |

---

## Getting Started

### Prerequisites

-   **Python**: 3.10 or higher
-   **Node.js**: 18.0.0 or higher
-   **npm**: 9.0.0 or higher

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MoMakkawi/Agentic_tracking_system
    cd Agentic_tracking_system
    ```

2.  **Install Python specific dependencies (Utils & API):**
    ```bash
    # Install utils
    cd utils
    pip install -e .
    cd ..
    ```

3.  **Install Frontend dependencies:**
    ```bash
    cd dashboard
    npm install
    cd ..
    ```

### Running the System

To start the entire system (API + Dashboard) simultaneously, use the provided runner script:

```bash
python run.py
```

This command will:
1.  Start the FastAPI backend on `http://localhost:8000`.
2.  Start the React Dashboard on `http://localhost:5173`.
3.  Stream logs from both services to your terminal.

---

## Configuration

The system uses a centralized `config.json` file for managing behavior.

-   **Location**: Root directory or `utils` package.
-   **Hot-Reloading**: Changes to `config.json` are applied immediately without restarting the server.
-   **Secrets**: API keys and sensitive data should be managed via environment variables or the secure `Secrets.py` module.

---

## Development

-   **Backend**: The API documentation is available at `http://localhost:8000/docs` (Swagger UI) when the server is running.
-   **Frontend**: The dashboard supports HMR (Hot Module Replacement) for rapid development.
-   **Agents**: New agents can be registered in the Orchestrator's configuration.

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.
