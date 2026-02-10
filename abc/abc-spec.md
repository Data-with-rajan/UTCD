# ABC – Agent Behavior Contract Specification (v0.1)

**Status:** Draft / v0.1-alpha  
**Parent Project:** [UTCD (Universal Tool Capability Descriptor)](../README.md)  
**Vision:** Define a lightweight, enforceable, execution-agnostic contract that governs how AI agents behave when using UTCD-defined tools.

---

## 1. Introduction

ABC (Agent Behavior Contract) is a focused enforcement layer that complements UTCD. While UTCD describes what a tool *can* do (Capability Layer), ABC defines how an agent *must* behave when using those tools (Behavior Layer).

## 2. Core Principles

- **Minimalism:** v0.1 focuses on the most critical behavioral constraints.
- **UTCD-Dependency:** ABC contracts only reference tools defined via UTCD.
- **Determinism-First:** Encourages predictable agent execution.
- **Safety Inheritance:** ABC risk levels are derived from and validated against UTCD tool metadata.

## 3. Contract Layers

An ABC contract is composed of 8 distinct layers:

### 3.1 Identity Layer
Defines the unique identity and version of the contract.
- `contract_id`: URN format (e.g., `urn:abc:researcher:v1`).
- `version`: Semantic versioning.
- `description`: Human-readable purpose.

### 3.2 Mission Layer
Defines the objective context for the agent.
- `primary_goal`: The core mission of the agent.
- `measurable_metrics`: (Optional) KPIs for success.

### 3.3 Cognition Constraints
Reasoning boundaries for the agent's internal logic.
- `reasoning_mode`: `reactive` (immediate response) or `deliberative` (multi-step planning).
- `max_reasoning_depth`: Maximum number of internal reasoning loops.
- `reflection_allowed`: Boolean flag for self-correction loops.

### 3.4 Tool Integration (UTCD)
**MANDATORY.** ABC does not define tools; it references UTCD tools.
- `reference_type`: Must be `utcd`.
- `allowed_tools`: List of UTCD identifiers (e.g., `utcd:web-search:v1`).

### 3.5 Execution Boundaries
Limits on the agent's interaction with the environment.
- `deterministic`: If true, the agent must use fixed seeds or temperature 0.
- `max_tool_calls`: Ceiling on total tool invocations per session.
- `timeout_seconds`: Hard limit on execution time.
- `token_budget`: Maximum LLM tokens allowed for the entire task.

### 3.6 Cost & Resource Control
(Optional) Economic and resource limits.
- `max_external_calls`: Limit on API calls outside the primary toolset.
- `max_parallel_actions`: Maximum simultaneous tool executions.

### 3.7 Risk & Safety Enforcement
Inheritance of risk signals from UTCD.
- `risk_level`: `low`, `medium`, or `high`.
- `require_sandbox`: Enforce execution in a restricted environment.
- `logging_required`: Mandate detailed audit logs for every action.

### 3.8 Ethics Guardrails
Hard constraints on agent intent.
- `no_deception`: Agent must not mislead users or external systems.
- `no_sensitive_data_extraction`: Prohibit attempts to bypass privacy controls.
- `transparency_required`: Mandate that the agent identifies itself as an AI and declares its contract bounds if asked.

### 3.9 Governance Layer (Enterprise Ready)
Advanced controls for compliance and oversight.
- `hitl_required`: Boolean. If true, high-impact tool calls require manual human approval.
- `memory_policy`: `stateless` (wipe after task), `session` (persist during run), or `persistent` (long-term learning).
- `data_residency`: List of allowed jurisdictions for data processing (e.g., `["EU", "US"]`).

---

## 4. Validation Rules

A validator must enforce the following:
1. **Schema Compliance:** The contract must match the `abc-schema.json`.
2. **UTCD Verification:** All `allowed_tools` must be valid UTCD descriptors.
3. **Risk Parity:** The contract `risk_level` must be compatible with the aggregate risk of the allowed tools.
4. **Budget Enforcement:** Runtimes must proactively terminate agents exceeding `max_tool_calls` or `token_budget`.

## 5. Ecosystem Positioning

| Layer | Responsibility | Standard |
|-------|----------------|----------|
| **Capability** | Tool Description | UTCD |
| **Behavior** | Execution Governance | **ABC** |
| **Workflow** | Task Orchestration | Oracle / OSSA |
| **Runtime** | Execution Environment | MCP Server |
