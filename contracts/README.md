# 🎭 Agent Behavior Contract (ABC)

ABC is the behavioral governance layer of the AI Agent Contract Stack. It defines **how** an agent must behave when using tools defined by [UTCD](../README.md).

## 📁 Directory Structure

- `contract-spec.md`: The formal v1.0 specification.
- `contract-schema.json`: The JSON Schema for validating `.contract.yaml` files.
- `GOVERNANCE.md`: Deep-dive into HITL, Memory, and Data Residency.
- `examples/`: Tiered contract examples (Research, Analytics, External Action, EU-Secure).

## 🚀 Usage

### 1. Validate a Contract
Use the built-in validator to ensure your behavior contract is valid and respects tool risk inheritance:

```bash
python -m utcd.contract_validator examples/research-agent.contract.yaml
```

### 2. Create Your Own Contract
Copy an example from `examples/` and modify it. Ensure your `contract_id` follows the URN format: `urn:abc:<agent-name>:<version>`.

## 🛡️ Governance Extensions
ABC v1.0 includes enterprise-ready features:
- **HITL**: Manual approval for high-risk tools.
- **Memory**: Control over state persistence (`stateless` | `session` | `persistent`).
- **Residency**: Geofencing reasoning data (e.g., `["EU"]`).

For implementation details, see [GOVERNANCE.md](GOVERNANCE.md).
