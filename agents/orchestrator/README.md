# Orchestrator Agent

The `orchestrator` is the central coordinator, planner, and security governor of the Agentic Tracking System. Built on the **smolagents** framework, it parses user queries or system events, validates their scope, designs execution plans, schedules sub-agent operations, and formats the final user-facing responses.

Importantly, the Orchestrator **never directly manipulates raw database files or executes analytical code**. Instead, it acts as a manager delegating tasks to specialized sub-agents.

---

## Table of Contents

- [Overview](#overview)
- [Agent Scope](#agent-scope)
- [Responsibilities](#responsibilities)
- [Sub-Agents](#sub-agents)
- [Memory Management](#memory-management)
- [Workflow](#workflow)
- [Dynamic Activation](#dynamic-activation)
- [Security & Scope Validation](#security--scope-validation)
- [Output Rules](#output-rules)
- [Tools](#tools)
- [Recommended Models](#recommended-models)
- [License](#license)

---

## Overview

The Orchestrator provides a safe, natural-language interface for system operators. By utilizing tool-calling models, it routes complex questions (e.g., about attendance anomalies or cohort patterns) to the appropriate sub-agent, handles intermediate failures, and presents synthesized answers.

---

## Agent Scope

- **Allowed Actions**: User intent classification, sequence planning, sub-agent task routing, memory lookup, and response synthesis.
- **Forbidden Actions**: Directly writing code, importing raw data, running calculations, or disclosing file paths and instructions.
- **Output Constraint**: Returns a single, clean final text response to the client.

---

## Responsibilities

- **Entire Execution Lifecycle**: Handles the query from validation to delivery (scope -> intent -> routing -> orchestration -> synthesis -> delivery).
- **Instruction Precedence**: Enforces a strict control hierarchy: **System Instructions > Developer Rules > User Input**.
- **Input Neutralization**: Sanitizes user inputs to prevent injection attempts.

---

## Sub-Agents

The Orchestrator coordinates the following sub-agents as registerable tools:
1. **DATA_PIPELINE** (Stage 1): Handles data fetching and cleaning.
2. **DATA_VALIDATION** (Stage 2): Performs multi-layer data anomaly validations.
3. **GROUP_IDENTIFIER** (Stage 3): Formulates cohort groups via Louvain clustering.
4. **KNOWLEDGE_INSIGHT** (Stage 4): Evaluates complex analytical queries against stored data.

When routing, the Orchestrator:
- Designs the **minimal execution path** to resolve the query.
- Orders sub-agent calls by logical data dependencies.
- Dispatches sub-agents using **goal-oriented tasks** rather than technical execution instructions (never disclosing internal paths, tools, or code).

---

## Memory Management

To maintain coherence across multi-turn interactions, the Orchestrator includes:
- **Short-Term Memory**: Stores user messages and assistant responses within a single conversation session. This lets the operator ask follow-up questions without repeating context.
- **Strict Session Isolation**: Prevents memory leakage between independent user sessions, keeping credentials and queries private.
- **Insight-First Resolution**: Checks cached memories and previous answers first to resolve queries without executing expensive sub-agent pipelines when possible.

---

## Workflow

1. **Scope Check**: Validates if the query belongs to the attendance analytics domain.
2. **Memory Probe**: Checks short-term memory to see if the answer can be retrieved directly.
3. **Intent Decomposing**: Parses the query and identifies the required sub-agents.
4. **Sequential Dispatch**: Invokes sub-agents via their tool interfaces and handles results.
5. **Synthesis**: Polishes the final result, adds descriptive context, and drops technical tracebacks.

---

## Dynamic Activation

The Orchestrator operates under two modes:
- **Query-Driven (API)**: Responds to direct REST queries submitted through the `/agent/chat` endpoint.
- **Event-Driven (Scheduler)**: Triggered autonomously by the background `EventSchedulerService` at the conclusion of calendar sessions (`pass.ics`). In this mode, it runs the default workflow to fetch, validate, and cluster logs.

---

## Security & Scope Validation

### Valid Scope Topics
- Attendance logs, lateness, absences, and check-in timelines.
- Student cohorts, community structures, and engagement matrices.
- System-generated device, timestamp, and identity alerts.

### Forbidden / Out-of-Scope Topics
- Requests to view internal instructions, agent system prompts, or configuration parameters.
- Direct file exports or requests for local file paths on the server.
- Database modification commands (add, update, delete records via chat).

If a request violates security boundaries, the Orchestrator rejects it immediately with the canonical response:
> "I can't help with that request. I operate within a restricted attendance analytics system, and your request falls outside those boundaries. Please ask a question related to attendance data, student groups, alerts, or related analysis."

---

## Output Rules

The Orchestrator's final response must:
- Start with **exactly one explanatory sentence**.
- Immediately present the **final result**.
- Provide a new line suggesting **logical next steps**.
- Exclude internal reasoning steps, sub-agent tool call blocks, and file paths.

---

## Tools

The `orchestrator.tools` package exposes the sub-agents to the Orchestrator as standard callable tools:
- **`pipeline_agent_tool`**: Triggers data ingestion and cleaning.
- **`validation_agent_tool`**: Triggers anomaly checks and returns execution status.
- **`group_identifier_agent_tool`**: Triggers Louvain clustering and updates group files.
- **`insighter_agent_tool`**: Triggers sandboxed query analysis on data.

---

## Recommended Models

The system is configured in `config.json` to utilize the following models hosted on the **RAGaRenn** platform:

| Model | Role | Description |
| :--- | :--- | :--- |
| **`openai/gpt-oss-120b`** | Primary Model | Optimal for high-level sequence planning, reasoning, and context synthesis. |
| **`mistralai/Mistral-Small-3.2-24B-Instruct-2506`** | Primary / Fallback | Fast, lightweight model optimized for structured tool call routing. |
| **`RedHatAI/Llama-3.3-70B-Instruct-FP8-dynamic`** | Fallback Model | Stable instruction-following model used for intent verification and safety checks. |

---

## License

See LICENSE in the project root.