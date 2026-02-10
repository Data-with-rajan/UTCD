# ABC Governance Layer – Technical Guide

The **ABC Governance Layer** is an enterprise-ready extension that provides high-fidelity control over AI agent behavior. While the core ABC layers handle execution metrics, the Governance layer handles **Policy Compliance**.

---

## 1. Human-in-the-Loop (HITL) Triggers

The `hitl_required` field defines whether an agent is allowed to execute high-impact tool calls autonomously.

- **`hitl_required: true`**: The runtime **must** intercept tool calls and request manual human approval before execution. This is recommended for:
  - Financial transactions
  - System-level deployment
  - PII extraction
- **`hitl_required: false`**: The agent can execute tools autonomously within its budget.

## 2. Memory Persistence Policy

The `memory_policy` field defines the lifecycle of an agent's internal state and learned context. This is a critical privacy and security control.

| Policy | Lifecycle | Use Case |
|--------|-----------|----------|
| **`stateless`** | Wiped after every task | Highly secure research, PII processing |
| **`session`** | Persists during a single run | Multi-step workflows (e.g., recursive search) |
| **`persistent`** | Long-term memory storage | Personal assistants, long-term learning agents |

> [!WARNING]
> Using `persistent` memory requires a compatible runtime that supports encrypted vector stores and audited retrieval.

## 3. Data Residency (Geofencing)

The `data_residency` field mandates the jurisdictions where the agent’s reasoning and tool data processing are allowed to occur.

- **Example**: `data_residency: ["EU", "US"]`
- runtimes must ensure the LLM inference and the tools themselves reside in the specified regions. This ensures compliance with **GDPR**, **CCPA**, and other local data laws.

## 4. Implementation Example

```yaml
# A secure, EU-compliant analytics agent
identity:
  contract_id: "urn:abc:secure-analyst:v1"

governance:
  hitl_required: true
  memory_policy: "stateless"
  data_residency: ["EU"]
```

---

## 5. Validator Enforcement

The `abc validate` command ensures these fields are present and follow the semantic rules defined in `abc-schema.json`. Runtimes that support ABC are expected to kill any agent process that attempts to bypass these constraints (e.g., an EU-only agent attempting to call a US-based API).
