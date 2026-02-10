<p align="center">
  <img src="assets/logo.png" alt="UTCD Logo" width="120">
</p>

<h1 align="center">The AI Agent Contract Stack</h1>

<p align="center">
  <strong>The minimal, execution-agnostic governance framework for machine intelligence.</strong><br>
  <strong>UTCD</strong> (Capability Layer) + <strong>ABC</strong> (Behavior Layer)
</p>

---



## �️ The Mechanism

The stack separates **Capability** (what a tool is) from **Behavior** (how it's used).

### 1. UTCD (Capability Layer)
A YAML-based "nutrition label" for tools. It lets tools describe themselves so agents can reason about them **before execution**.

```yaml
utcd_version: "1.0"
identity:
  name: "Web Search"
capability:
  domain: "search"
constraints:
  side_effects: ["net:http-outbound"]
```

### 2. Agent Behavior Contract (ABC)
The enforceable contract that governs agent behavior. Defined by the ABC standard and stored in the `contracts/` directory.

```yaml
identity:
  contract_id: "urn:abc:researcher:v1"
tools:
  reference_type: "utcd"
  allowed_tools: ["utcd:web-search:v1"]
execution:
  max_tool_calls: 5
governance:
  hitl_required: true   # Human-in-the-loop
```

## 🛠️ CLI Usage

The stack provides two primary validators to ensure your descriptors and contracts are production-ready.

### 1. Tool Capability Validation (UTCD)
Ensures a tool's "Nutrition Label" follows the standard schema.
```bash
python -m utcd.validator examples/csv-analyzer.utcd.yaml
```

#### 2. Validate Behavioral Integrity (ABC)
Ensure an **Agent Behavior Contract** is valid and respects tool risk inheritance:
```bash
python -m utcd.contract_validator contracts/examples/research-agent.contract.yaml
```

### Use the Agent

```python
from utcd import UTCDAgent, UTCDLoader, Policy

# Create agent with GDPR policy
agent = UTCDAgent(policy=Policy.gdpr())

# Load tools
agent.load_tools_from_directory("./examples")

# Find the safest data processing tool
results = agent.find_tools(domain="data-processing")
best = results[0]

print(f"Selected: {best.tool_name}")
print(f"Score: {best.score}/100")
```

### Run Demos

```bash
python demos/demo_selection.py     # Tool selection
python demos/demo_rejection.py     # Tool rejection
python demos/demo_degradation.py   # Graceful degradation
```

## 📁 Project Structure

```
UTCD/
├── schema/                    # JSON Schema definitions
│   ├── utcd-core.schema.json  # Core schema (frozen)
│   └── profiles/              # Optional profile schemas
├── utcd/                      # Python package
│   ├── loader.py              # Load UTCD files
│   ├── validator.py           # Validate UTCD files
│   ├── contract_validator.py  # Validate behavior contracts
│   └── agent.py               # Reasoning agent
├── examples/                  # Example UTCD files
├── contracts/                 # Agent Behavior Contracts (ABC)
│   ├── contract-spec.md       # Formal specification
│   ├── contract-schema.json   # JSON Schema for contracts
│   └── examples/              # Example .contract.yaml contracts
├── demos/                     # Demo scripts
└── tests/                     # Unit tests
```

## 🔐 Built-in Policies

| Policy | Description |
|--------|-------------|
| `Policy.strict()` | No side effects, no data retention |
| `Policy.standard()` | Balanced safety defaults |
| `Policy.permissive()` | Warnings only, no rejections |
| `Policy.gdpr()` | EU data residency, encryption required |

## 📖 Core Principles

1. **Pre-execution only** — UTCD describes, never executes
2. **Static & declarative** — No runtime dependencies
3. **Offline-valid** — Works without network
4. **Human + machine readable** — YAML format
5. **Minimal core, optional profiles** — Core is frozen, profiles evolve

## 🔗 Discovery Tiers

| Tier | Mechanism | Status |
|------|-----------|--------|
| 1 | Shipped with tool (`utcd.yaml`) | ✅ MUST |
| 2 | Well-known URL (`/.well-known/utcd.yaml`) | ✅ SHOULD |
| 3 | Embedded reference in manifest | ⚠️ MAY |
| 4 | Central registry | ❌ NEVER REQUIRED |
| 5 | Future Roadmap | [Roadmap](FUTURE_ROADMAP.md) |

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

**UTCD is infrastructure, not a product.** It's designed to be easy to publish, easy to ignore, and impossible to misuse safely.
