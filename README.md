<p align="center">
  <img src="assets/logo.png" alt="UTCD Logo" width="120">
</p>

<h1 align="center">UTCD — Universal Tool Capability Descriptor</h1>

<p align="center">
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+"></a>
</p>

<p align="center">
  <strong>A minimal, execution-agnostic, open descriptor system that allows AI agents to discover, evaluate, and reason about tools before execution.</strong>
</p>

---



## 🎯 What is UTCD?

UTCD is a YAML-based specification that lets tools describe themselves to AI systems. Think of it as a "nutrition label" for AI tools.

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

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/your-org/utcd.git
cd utcd

# Install dependencies
pip install pyyaml
```

### Validate a UTCD file

```bash
python -m utcd.validator examples/csv-analyzer.utcd.yaml
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
│   └── agent.py               # Reasoning agent
├── examples/                  # Example UTCD files
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

## 📄 License

MIT License - See [LICENSE](LICENSE) for details.

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

---

**UTCD is infrastructure, not a product.** It's designed to be easy to publish, easy to ignore, and impossible to misuse safely.
