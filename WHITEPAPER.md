# UTCD Whitepaper

**Universal Tool Capability Descriptor**

*A Cognitive Interoperability Layer for AI-Tool Interaction*

Version 1.0 | January 2025

---

## Executive Summary

As AI agents become primary orchestrators of software tools, a critical gap exists: **there is no standard way for tools to describe their capabilities, constraints, and trustworthiness to AI systems**.

UTCD (Universal Tool Capability Descriptor) fills this gap with a minimal, execution-agnostic specification that enables AI agents to discover, evaluate, and reason about tools **before execution**.

UTCD is not a platform, runtime, or marketplace. It is **infrastructure** — designed to be easy to publish, easy to ignore, and impossible to misuse safely.

---

## Table of Contents

1. [The Problem](#1-the-problem)
2. [The Solution](#2-the-solution)
3. [Design Principles](#3-design-principles)
4. [Architecture](#4-architecture)
5. [Core Schema](#5-core-schema)
6. [Optional Profiles](#6-optional-profiles)
7. [Discovery Model](#7-discovery-model)
8. [Agent Reasoning](#8-agent-reasoning)
9. [Comparison with Existing Standards](#9-comparison-with-existing-standards)
10. [Governance & Evolution](#10-governance--evolution)
11. [Use Cases](#11-use-cases)
12. [Roadmap](#12-roadmap)
13. [Conclusion](#13-conclusion)

---

## 1. The Problem

### The Rise of AI Agents

AI agents are evolving from simple chatbots to autonomous systems that:
- Execute multi-step workflows
- Select and invoke external tools
- Make decisions on behalf of users
- Operate in regulated environments

### The Trust Gap

Currently, when an AI agent needs to use a tool, it faces a fundamental problem:

| Question | Current State |
|----------|--------------|
| "What does this tool do?" | Agent guesses or trusts documentation |
| "Is it safe to use?" | Unknown until execution |
| "Does it comply with our policies?" | Manual review required |
| "Where does my data go?" | Often undisclosed |
| "How much will it cost?" | Discovered after the fact |

**Result:** AI agents either operate blindly or require extensive manual vetting.

### The Fragmentation Problem

Multiple protocols exist for tool execution (MCP, A2A, ACP, OpenAI Functions), but none addresses the **pre-execution** question:

> "What should I know about this tool before I decide to use it?"

---

## 2. The Solution

UTCD provides a **declarative, static, machine-readable** format for tools to describe themselves.

```yaml
utcd_version: "1.0"

identity:
  name: "CSV Analyzer"
  purpose: "Analyze CSV data with statistical methods"

capability:
  domain: "data-processing"
  inputs: ["csv_file", "analysis_type"]
  outputs: ["statistics", "charts"]

constraints:
  side_effects: ["none"]
  data_retention: "none"

connection:
  modes:
    - type: "http"
      detail: "https://api.example.com/analyze"
```

An AI agent reading this descriptor immediately knows:
- ✅ What the tool does
- ✅ What inputs/outputs to expect
- ✅ No side effects (safe)
- ✅ No data retention (privacy-safe)
- ✅ How to connect to it

---

## 3. Design Principles

UTCD is built on non-negotiable principles:

| Principle | Meaning |
|-----------|---------|
| **Pre-execution only** | Describes, never executes |
| **Static & declarative** | YAML files, no runtime logic |
| **Offline-valid** | Works without network access |
| **Human + machine readable** | Understandable by both |
| **Minimal unbreakable core** | Frozen after v1 |
| **Optional complexity via profiles** | Opt-in extensions |
| **No central authority** | Decentralized discovery |
| **No forced monetization** | Free to implement |

**If any proposal violates these principles, it is rejected.**

---

## 4. Architecture

```
┌─────────────────────────────────────────┐
│              UTCD Core                  │ ← Mandatory, frozen
│     (identity, capability, constraints) │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│            UTCD Profiles                │ ← Optional, composable
│    (security, privacy, cost, etc.)      │
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│           UTCD Extensions               │ ← Experimental
│      (community-driven additions)       │
└─────────────────────────────────────────┘
```

This layered architecture mirrors successful standards like Linux, TCP/IP, and Kubernetes.

---

## 5. Core Schema

The core schema is **mandatory** and **frozen after v1**.

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `utcd_version` | string | Specification version ("1.0") |
| `identity.name` | string | Human-readable tool name |
| `identity.purpose` | string | What the tool does |
| `capability.domain` | string | Primary domain (e.g., "communication") |
| `capability.inputs` | array | Input types accepted |
| `capability.outputs` | array | Output types produced |
| `constraints.side_effects` | array | Side effects (e.g., ["none"], ["io:filesystem-read"]) |
| `constraints.data_retention` | enum | "none" \| "session" \| "persistent" |
| `connection.modes` | array | Connection methods with type + detail |

### Side Effects Vocabulary (Recommended)

UTCD recommends but does not mandate these values:

```
none                    # No side effects
io:filesystem-read      # Reads local files
io:filesystem-write     # Writes local files
net:http-outbound       # Makes HTTP requests
net:http-inbound        # Receives HTTP requests
process:spawn           # Spawns processes
hw:gpu                  # Uses GPU resources
hw:camera               # Accesses camera
hw:microphone           # Accesses microphone
```

Agents treat unknown values as potentially unsafe by default.

---

## 6. Optional Profiles

Profiles extend core descriptors with domain-specific metadata.

### Security Profile

```yaml
security:
  fingerprint: "sha256:abc123..."
  publisher: "did:web:example.com"
  signatures:
    - alg: "ed25519"
      sig: "base64..."
```

**Purpose:** Trust verification, anti-spoofing, supply chain security

### Privacy Profile

```yaml
privacy:
  data_location: ["EU"]
  encryption: ["in-transit", "at-rest"]
  pii_handling: "anonymized"
  data_deletion: "immediate"

compliance:
  standards: ["GDPR", "SOC2-Type2"]
```

**Purpose:** GDPR compliance, enterprise governance, regulatory requirements

### Cost Profile

```yaml
cost:
  model: "pay-per-call"
  currency: "USD"
  estimates:
    - input: "1MB"
      cost: "0.01 USD"
      latency_p50: "200ms"
```

**Purpose:** Cost-aware agent decisions, budget enforcement

---

## 7. Discovery Model

UTCD uses **plural discovery**, not central discovery.

| Tier | Mechanism | Status | Description |
|------|-----------|--------|-------------|
| 1 | Shipped with tool | ✅ MUST | `utcd.yaml` in repo/package |
| 2 | Well-known URL | ✅ SHOULD | `/.well-known/utcd.yaml` |
| 3 | Embedded reference | ⚠️ MAY | Pointer in package.json, etc. |
| 4 | Central registry | ❌ NEVER REQUIRED | Optional convenience |

**This design prevents capture by any single entity.**

```
Think DNS, not App Store.
```

---

## 8. Agent Reasoning

UTCD enables policy-based tool selection:

### Example: GDPR Policy

```python
from utcd import UTCDAgent, Policy

agent = UTCDAgent(policy=Policy.gdpr())
agent.load_tools_from_directory("./available-tools")

# Find compliant data processing tool
results = agent.find_tools(
    domain="data-processing",
    require_compliance=["GDPR"]
)

best_tool = results[0]
print(f"Selected: {best_tool.name} (score: {best_tool.score}/100)")
```

### Decision Types

| Decision | Meaning |
|----------|---------|
| `APPROVED` | Tool passes all policy rules |
| `WARNING` | Tool passes with non-critical concerns |
| `REJECTED` | Tool violates one or more policy rules |

### Graceful Degradation

Agents SHOULD still evaluate tools missing optional profiles:

```
Tool without privacy profile → Treat as "unknown privacy"
Tool without cost profile → Treat as "unknown cost"
Tool without security profile → Warn but don't reject
```

---

## 9. Comparison with Existing Standards

| Standard | Purpose | Relationship to UTCD |
|----------|---------|---------------------|
| **MCP** (Anthropic) | Tool execution protocol | UTCD describes; MCP executes |
| **A2A** (Google) | Agent-to-agent communication | UTCD can be embedded |
| **OpenAI Functions** | Function calling schema | Only defines inputs/outputs, no trust |
| **OpenAPI** | REST API description | Similar concept, different domain |
| **Model Cards** | ML model metadata | Equivalent for models, not tools |

**UTCD sits above execution protocols**, providing metadata that informs the decision to execute.

```
┌─────────────────────────────────────────┐
│              UTCD (Descriptor)          │ ← What the tool IS
└─────────────────────────────────────────┘
                    │
                    ▼
┌─────────────┬─────────────┬─────────────┐
│     MCP     │     A2A     │   OpenAI    │ ← How to INVOKE
└─────────────┴─────────────┴─────────────┘
```

---

## 10. Governance & Evolution

### Core Governance

- Core schema **frozen after v1**
- Breaking changes require new major version
- Backward compatibility required

### Profile Governance

- Profiles evolve independently
- Community-driven additions
- Reference implementations required before adoption

### Non-Goals

- ❌ No central authority
- ❌ No mandatory registry
- ❌ No corporate control
- ❌ No standards body lock-in

---

## 11. Use Cases

### Enterprise AI Governance

> "Only allow our AI agents to use tools that don't retain data and are GDPR compliant."

UTCD enables automated policy enforcement across all AI systems.

### AI Agent Safety

> "My agent should never use a tool that can write to the filesystem."

Agents can filter tools by `side_effects` before execution.

### Tool Marketplace

> "Show me all tools for data processing, sorted by cost."

Marketplaces can query UTCD metadata for discovery and comparison.

### Compliance Audit

> "Prove that our AI systems only used approved tools."

UTCD provides auditable metadata for every tool decision.

### Multi-Agent Coordination

> "Agent A shares its available tools with Agent B."

Agents exchange UTCD descriptors to coordinate capabilities.

---

## 12. Roadmap

### Phase 1: Foundation (Complete ✓)
- Core schema specification
- Reference validator
- Reference agent
- Example tools and demos

### Phase 2: Adoption (In Progress)
- GitHub public release
- Integration with LangChain
- Integration with CrewAI
- Blog post: "Why UTCD"

### Phase 3: Ecosystem (Planned)
- MCP integration
- Community profile contributions
- Enterprise governance tools
- Certification program

### Phase 4: Maturity (Future)
- Official v1.0 release
- Multiple language implementations
- Industry adoption

---

## 13. Conclusion

UTCD is **infrastructure, not a product**.

It solves a fundamental problem: **AI agents need to understand tools before using them.**

By providing a minimal, open, execution-agnostic standard, UTCD enables:
- Safer AI agent operations
- Enterprise governance and compliance
- Tool discoverability and comparison
- Graceful degradation and trust reasoning

UTCD is designed to be:
- **Easy to publish** — just a YAML file
- **Easy to ignore** — optional profiles, no mandates
- **Impossible to misuse safely** — declarative, no execution

---

## Appendix A: Full Core Schema

```yaml
utcd_version: "1.0"

identity:
  name: string
  purpose: string

capability:
  domain: string
  inputs: [string]
  outputs: [string]

constraints:
  side_effects: [string]
  data_retention: "none" | "session" | "persistent"

connection:
  modes:
    - type: string
      detail: string
```

---

## Appendix B: Reference Implementation

Available at: `github.com/[your-org]/utcd`

- Python package: `utcd`
- CLI validator: `python -m utcd.validator <file.yaml>`
- Agent library: `from utcd import UTCDAgent, Policy`

---

## License

This specification and reference implementation are released under the MIT License.

UTCD is an open standard. No permission required to implement.

---

*UTCD is a cognitive interoperability layer, not a platform. That framing avoids power struggles, vendor resistance, and premature monetization.*
