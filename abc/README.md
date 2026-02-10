# 🎭 ABC (Agent Behavior Contract)

ABC is the behavioral governance layer of the AI Agent Contract Stack. It defines **how** an agent must behave when using tools defined by [UTCD](../README.md).

## 📁 Directory Structure

- `abc-spec.md`: The formal v0.1 specification.
- `abc-schema.json`: The JSON Schema for validating `.abc.yaml` files.
- `GOVERNANCE.md`: Deep-dive into HITL, Memory, and Data Residency.
- `examples/`: Tiered contract examples (Research, Analytics, External Action, EU-Secure).

## 🚀 Usage

### 1. Validate a Contract
Use the built-in validator to ensure your behavior contract is valid:

```bash
python -m utcd.abc_validator examples/research-agent.abc.yaml
```

### 2. Create Your Own Contract
Copy an example from `examples/` and modify it. Ensure your `contract_id` follows the URN format: `urn:abc:<agent-name>:<version>`.

## 🛡️ Governance Extensions
ABC v0.1 includes enterprise-ready features:
- **HITL**: Manual approval for high-risk tools.
- **Memory**: Control over state persistence (`stateless` | `session` | `persistent`).
- **Residency**: Geofencing reasoning data (e.g., `["EU"]`).

For implementation details, see [GOVERNANCE.md](GOVERNANCE.md).
