# UTCD Specification v1.0

**Universal Tool Capability Descriptor**

Status: Open specification | Vendor-neutral | Execution-agnostic

---

## 1. Purpose

UTCD defines how tools describe themselves to intelligence — **before execution**.

UTCD enables AI systems, agents, and humans to:
- Discover tools
- Understand capabilities  
- Evaluate safety & constraints
- Compare alternatives
- Decide whether to execute

UTCD does **not**:
- Execute tools
- Orchestrate workflows
- Replace APIs, MCP, A2A, ACP, plugins
- Mandate infrastructure

---

## 2. Core Design Principles

| Principle | Meaning |
|-----------|---------|
| Pre-execution only | Describes, never runs |
| Static & declarative | No runtime dependencies |
| Offline-valid | Works without network |
| Human + machine readable | YAML format |
| Minimal core | Frozen after v1 |
| Optional profiles | Composable extensions |
| No central authority | Decentralized discovery |

---

## 3. Architecture

```
UTCD Core        → mandatory, frozen
UTCD Profiles    → optional, composable  
UTCD Extensions  → experimental
```

---

## 4. UTCD Core Schema

**File name:** `utcd.yaml` or `*.utcd.yaml`

### Required Fields

```yaml
utcd_version: "1.0"

identity:
  name: string          # Human-readable name
  purpose: string       # What the tool does

capability:
  domain: string        # Primary domain
  inputs: [string]      # Input types accepted
  outputs: [string]     # Output types produced

constraints:
  side_effects: [string]      # e.g. ["none"], ["io:filesystem-read"]
  data_retention: string      # "none" | "session" | "persistent"

connection:
  modes:
    - type: string      # "cli" | "http" | "mcp" | "grpc" | "other"
      detail: string    # Connection details
```

### Side Effects Vocabulary (Recommended)

| Effect | Description |
|--------|-------------|
| `none` | No side effects |
| `io:filesystem-read` | Reads local files |
| `io:filesystem-write` | Writes local files |
| `net:http-outbound` | Makes HTTP requests |
| `process:spawn` | Spawns processes |
| `hw:gpu` | Uses GPU resources |

Free-form values are allowed. Agents treat unknown values as potentially unsafe.

---

## 5. Optional Profiles

### 5.1 Security Profile

```yaml
security:
  fingerprint: "sha256:..."
  publisher: "did:web:example.com"
  signatures:
    - alg: "ed25519"
      key_id: "did:web:example.com#key-1"
      sig: "base64..."
```

### 5.2 Privacy Profile

```yaml
privacy:
  data_location: ["EU", "US"]
  encryption: ["in-transit", "at-rest"]
  pii_handling: "none" | "anonymized" | "pseudonymized" | "stored"
  data_deletion: "immediate" | "on-request" | "scheduled" | "never"

compliance:
  standards: ["GDPR", "SOC2-Type2", "HIPAA"]
```

### 5.3 Cost Profile

```yaml
cost:
  model: "free" | "pay-per-call" | "subscription" | "usage-based"
  currency: "USD"
  estimates:
    - input: "1MB"
      cost: "0.01 USD"
      latency_p50: "200ms"

performance:
  availability: "99.9%"
  rate_limit: "100/min"
```

---

## 6. Discovery

| Tier | Mechanism | Status |
|------|-----------|--------|
| 1 | Shipped with tool | ✅ MUST |
| 2 | `/.well-known/utcd.yaml` | ✅ SHOULD |
| 3 | Embedded reference | ⚠️ MAY |
| 4 | Registry | ❌ NEVER REQUIRED |

---

## 7. Agent Behavior

Agents SHOULD:
1. Load UTCD descriptors before execution
2. Apply policy rules to filter tools
3. Prefer tools with higher safety scores
4. Treat missing profiles as unknown (graceful degradation)
5. Explain rejection decisions

Agents MUST NOT:
1. Execute tools without reading descriptors
2. Trust tools solely based on descriptors
3. Ignore side_effects declarations

---

## 8. Versioning

- Core schema frozen after v1.0
- Profiles evolve independently
- Backward compatibility required
- Breaking changes require new major version

---

## 9. License

This specification is released under MIT License.

UTCD is an open standard. No permission required to implement.
