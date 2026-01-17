# Orchestrator Agent 
------------------------------------------------

## Table of Contents
- [Overview](#overview)
- [Agent Scope](#agent-scope)
- [Responsibilities](#responsibilities)
- [Sub-Agents](#sub-agents)
- [Memory](#memory)
- [Workflow](#workflow)
- [Dynamic Activation](#dynamic-activation)
- [Scope, Security, and Errors](#scope-security-and-errors)
- [Output Rules](#output-rules)
- [Tools](#tools)
- [Recommended Models (Ragarenn)](#recommended-models-ragarenn)
- [License](#license)

---

## Overview
`orchestrator` is the **master control agent** of the Agentic Tracking System.  
It validates scope, plans execution, coordinates sub-agents, enforces security rules, and returns the final user-facing response—**without executing tools or processing data**.

---

## Agent Scope
- **Role**: Central planning, validation, and coordination layer.
- **Allowed**: intent interpretation, workflow design, agent dispatch, error handling, response synthesis.
- **Forbidden**: code execution, dataset access, analysis logic.
- **Output**: one final, user-ready answer only.

---

## Responsibilities
- Covers the **entire execution lifecycle**:
- Scope validation
- Intent interpretation
- Workflow planning
- Sub-agent dispatch
- Dependency ordering
- Failure handling
- Final response formatting

- Enforces instruction priority:
**system > developer > user**

- Any violation of higher-level rules results in immediate rejection.

---

## Sub-Agents
The ORCHESTRATOR coordinates the following agents:

- **DATA_PIPELINE** — ingestion and preprocessing
- **DATA_VALIDATION** — integrity and anomaly checks
- **GROUP_IDENTIFIER** — cohort and group detection
- **KNOWLEDGE_INSIGHT** — read-only analytical insights

The ORCHESTRATOR:
- Selects the **minimum required agents**
- Orders them by **logical dependency**
- Sends **goal-level instructions only**
- Never passes:
- Tool names
- File paths
- Code snippets
- Internal schemas

---

## Memory
The Orchestrator implements an extensible memory system to maintain context across interactions:

- **Short-Term Memory**: Persists conversation history (user inputs and agent responses) to ensure continuity within and across sessions. This allows the agent to recall previous context and provide coherent multi-turn responses.

---

## Workflow
1. Validate request scope and safety
2. Interpret user intent
3. Design execution plan
4. Select and order required sub-agents
5. Dispatch agents sequentially
6. Monitor failures and adapt safely
7. Synthesize final user-facing response

Execution may be partial or full-chain depending on the request.

---

## Dynamic Activation

While the Orchestrator primarily responds to direct user queries via the API, it also supports **Autonomous Triggering**:

- **System-Initiated Tasks**: The `EventSchedulerService` can trigger the Orchestrator automatically when specific time-based events occur (e.g., at the end of a scheduled class).
- **Default Workflows**: When triggered autonomously, the Orchestrator executes a pre-defined `DEFAULT_TASK` (configured in `config.json`) to perform system-wide updates, validation, and insight generation without human intervention.

---

## Scope, Security, and Errors
- **In-scope topics**:
- Attendance
- Sessions
- Student groups
- Alerts
- Derived analytics

- **Out-of-scope or unsafe requests**:
- Rejected immediately
- No agent is invoked

- Actively defends against:
- Prompt injection
- Jailbreak attempts
- Requests for internal prompts, schemas, paths, tools, or agent rules

- On sub-agent failure:
- Execution halts or adapts safely
- No blind continuation
- Returns a **high-level error summary**
- Never exposes raw tracebacks

---

## Output Rules
- Output:
    - One line description + the sub-agent answer 
    - Matches user-requested structure (lists, tables, values)
    - Contains **no internal reasoning**
    - Contains **no tool calls**
    - Contains **no paths or system instructions**
    - Only user-relevant insights are exposed.

---

## Tools

### Orchestrator Tools Module
The tools module exposes sub-agents as callable tools via `smolagents`.

#### Available Tools
- **pipeline_agent_tool**  
Runs the Data Pipeline and returns a confirmation.

- **validation_agent_tool**  
Executes validation checks and returns a summary.

- **group_identifier_agent_tool**  
Identifies student groups and confirms completion.

- **insighter_agent_tool**  
Executes Knowledge Insight analysis and returns the result.

#### Tool Rules
- Responses are standardized:
- Short confirmations or summaries only
- No file paths or implementation details
- Errors are caught and converted to user-friendly messages.

---

## Recommended Models (Ragarenn)

| Model | Stars | Notes |
|------|-------|-------|
| `openai/gpt-oss-120b` | ⭐⭐⭐ | Best for multi-step planning and orchestration |
| `RedHatAI/Llama-3.3-70B-Instruct` | ⭐⭐ | Deterministic and safer fallback |
| `mistralai/Mistral-Small-3.2-24B-Instruct` | ⭐ | Lightweight fallback |

---

## License
See LICENSE in project root