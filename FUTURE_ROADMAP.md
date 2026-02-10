# UTCD Future Roadmap 🚀

This document outlines the strategic direction and upcoming features for the **Universal Tool Capability Descriptor (UTCD)**.

---

## 🏗️ Phase 2: Technical Integrations (Current Focus)

The goal of Phase 2 is to make UTCD indispensable for agent developers by integrating with existing ecosystems.

- [ ] **MCP Bridge**: 
    - Create a tool that automatically generates `utcd.yaml` from MCP server definitions.
    - Export UTCD reasoning as MCP `metadata` or `capabilities`.
- [ ] **Agent Framework Plugins**:
    - `langchain-utcd`: A toolkit that automatically filters tools based on a `UTCDAgent` policy.
    - `crewai-utcd`: Seamless integration for CrewAI tool selection.
- [ ] **GitHub Action (UTCD-Linter)**: 
    - Automate validation of `utcd.yaml` files in PRs.
    - Enforce "Governance-as-Code" by failing builds that don't meet safety standards.

---

## 🎭 Phase 2.5: Agent Behavior Contract (ABC)

Defining the behavior layer for agent execution.

- [x] **Contract Specification**: Initial v1.0 release.
- [x] **Contract JSON Schema**: Standard core schema for behavior contracts.
- [x] **Contract Validator CLI**:
    - `python -m utcd.contract_validator`: Check schema compliance and tool risk inheritance.
- [ ] **Runtime Adapters**: Reference implementations for enforcing ABC constraints in agent runtimes.

---

## 🌐 Phase 3: Ecosystem & "UTCD Apps"

Transforming UTCD from a specification into a thriving ecosystem of utility applications.

### Potential "UTCD Apps" for the Community:
1. **UTCD Inspector (Web Tool)**:
    - A visual "Nutrition Label" generator. Paste a YAML, get a beautiful safety scorecard.
2. **The "Safe-Tool" Registry**:
    - A decentralized, searchable directory of tools indexed by their UTCD capabilities.
3. **Governance Dashboard**:
    - An enterprise internal tool for CISOs to monitor and set policies (e.g., "Block any tool that allows `net:http-outbound` without a Security Profile").
4. **UTCD Auto-Generator**:
    - AI-powered CLI scanning a function/API to write initial `utcd.yaml` drafts.

---

## 🛠️ Phase 4: Platform Maturity

Scaling the standard to be the default metadata layer for all machine intelligence.

- [ ] **Multi-Language Loaders**:
    - `utcd-js`: Reference implementation for Node.js and Browser environments.
    - `utcd-go`: High-performance loader for infrastructure tools.
- [x] **Cryptographic Verification**:
    - Implementation of the `Security Profile` with Ed25519 signatures in `UTCDDescriptor.verify_signatures()`.
- [ ] **Decentralized Identifiers (DID)**: Integration for publisher trust.
- [ ] **Interactive Reasoning**:
    - Enable "negotiation" where an agent can ask a tool for a more restricted UTCD (e.g., "Run this for me with a 'read-only' constraint").

---

## 📢 Promotion Strategy (Community Growth)

How to build a following when starting from zero:

1. **Guerilla Integration**:
    - Submit Pull Requests to popular open-source tools (e.g., small MCP servers) adding a `utcd.yaml`. This provides immediate value and visibility.
2. **"Complementary" Positioning**:
    - Avoid "UTCD vs MCP" messaging. Use "**UTCD + MCP**". Position UTCD as the *Safety Intelligence* that tells you *if* you should call the MCP tool.
3. **Technical Storytelling**:
    - Write a "The Pre-Execution Safety Gap" blog post on Hacker News and Reddit (r/LocalLLaMA). Focus on the "Cognitive Weights" philosophy.
4. **Awesome-UTCD List**:
    - Create a repository of "Awesome Tools with UTCD" to showcase early adopters.
5. **Developer DX**:
    - Build a VS Code extension for UTCD. Developers are more likely to adopt a standard if they have autocomplete and red-squiggles helping them.

---

*UTCD is infrastructure, not a product. It wins by being invisible, ubiquitous, and essential.*
