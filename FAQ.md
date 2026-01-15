# UTCD FAQ

**Frequently Asked Questions**

---

## General

### What is UTCD?

UTCD (Universal Tool Capability Descriptor) is a YAML-based specification that lets AI tools describe their capabilities, constraints, and trustworthiness in a machine-readable format.

### Who is UTCD for?

- **Tool developers** — Describe your tool's capabilities
- **AI agent developers** — Make informed tool selection decisions
- **Enterprises** — Enforce governance policies on AI tool usage
- **Platform builders** — Build tool marketplaces and registries

### Is UTCD free?

Yes. UTCD is open source under the MIT License. No permission required to implement.

---

## Technical

### Does UTCD execute tools?

**No.** UTCD is pre-execution only. It describes tools; it never runs them.

### What's the difference between UTCD and MCP?

| UTCD | MCP |
|------|-----|
| Describes what a tool IS | Describes how to CALL a tool |
| Static YAML file | Runtime protocol |
| Pre-execution reasoning | Execution transport |

They're complementary, not competing.

### What file format does UTCD use?

YAML. Files should be named `utcd.yaml` or `*.utcd.yaml`.

### What if a tool doesn't have all profiles?

UTCD supports **graceful degradation**. Missing profiles are treated as "unknown" rather than failures. Agents can still reason over core metadata.

---

## Discovery

### Where do UTCD files live?

UTCD uses plural discovery (like DNS):

1. **Shipped with tool** (MUST) — In the repo/package
2. **Well-known URL** (SHOULD) — `/.well-known/utcd.yaml`
3. **Reference in manifest** (MAY) — Pointer in package.json
4. **Registry** (NEVER REQUIRED) — Optional convenience

### Is there a central UTCD registry?

No, and there never will be. Registries may exist as convenience, but UTCD does not require or endorse any central authority.

---

## Adoption

### How do I add UTCD to my tool?

1. Create a `utcd.yaml` file in your project root
2. Fill in the core fields (identity, capability, constraints, connection)
3. Optionally add profiles (security, privacy, cost)
4. Validate with `python -m utcd.validator your-file.yaml`

### How do I use UTCD in my agent?

```python
from utcd import UTCDAgent, Policy

agent = UTCDAgent(policy=Policy.standard())
agent.load_tools_from_directory("./tools")

decision = agent.select_best(domain="data-processing")
```

---

## Governance

### Who controls UTCD?

No one. UTCD is an open standard with no central authority.

### Can the core schema change?

The core schema is **frozen after v1**. Only profiles can evolve.

### How do new profiles get added?

Community-driven. Propose a profile, provide a reference implementation, gather feedback, and it becomes adopted through usage — not decree.

---

## Comparison

### Why not just use OpenAPI?

OpenAPI describes **how to call an API** (endpoints, parameters). UTCD describes **what a tool is** (capabilities, safety, trust). Different purposes.

### Why not just use JSON?

YAML is more human-readable and supports comments. UTCD files are meant to be authored by humans and read by machines.

### How is this different from Model Cards?

Model Cards describe ML models. UTCD describes tools. Same philosophy, different domain.

---

## Business

### Can I build commercial products on UTCD?

Absolutely. The spec is open; what you build on top is yours.

### Does my company need to pay to use UTCD?

No. UTCD is free to implement, forever.
