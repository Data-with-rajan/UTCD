"""
UTCD Agent - Reasoning agent for tool selection and policy enforcement.
"""

from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum

from .loader import UTCDDescriptor, UTCDLoader


class NoSafeToolsException(Exception):
    """Raised when no tools pass the safety policy."""
    pass


class DecisionType(Enum):
    """Types of agent decisions."""
    APPROVED = "approved"
    REJECTED = "rejected"
    WARNING = "warning"


@dataclass
class PolicyRule:
    """A single policy rule."""
    name: str
    description: str
    check: Callable[[UTCDDescriptor], bool]
    severity: str = "error"  # "error" = reject, "warning" = warn but allow
    
    def evaluate(self, descriptor: UTCDDescriptor) -> bool:
        """Evaluate the rule against a descriptor. Returns True if rule passes."""
        return self.check(descriptor)


@dataclass
class Policy:
    """A collection of policy rules."""
    name: str
    rules: List[PolicyRule] = field(default_factory=list)
    
    def add_rule(self, rule: PolicyRule) -> "Policy":
        """Add a rule to the policy."""
        self.rules.append(rule)
        return self
    
    @staticmethod
    def strict() -> "Policy":
        """Create a strict policy that rejects unsafe tools."""
        policy = Policy(name="strict")
        
        # No side effects allowed
        policy.add_rule(PolicyRule(
            name="no-side-effects",
            description="Tool must have no side effects",
            check=lambda d: d.is_side_effect_free,
            severity="error"
        ))
        
        # No data retention
        policy.add_rule(PolicyRule(
            name="no-data-retention",
            description="Tool must not retain data",
            check=lambda d: not d.retains_data,
            severity="error"
        ))
        
        return policy
    
    @staticmethod
    def standard() -> "Policy":
        """Create a standard policy with reasonable defaults."""
        policy = Policy(name="standard")
        
        # Warn about side effects (don't reject)
        policy.add_rule(PolicyRule(
            name="side-effects-warning",
            description="Prefer tools without side effects",
            check=lambda d: d.is_side_effect_free,
            severity="warning"
        ))
        
        # Reject persistent data retention
        policy.add_rule(PolicyRule(
            name="no-persistent-retention",
            description="Tool must not persistently retain data",
            check=lambda d: d.constraints.data_retention != "persistent",
            severity="error"
        ))
        
        # Warn about missing security profile
        policy.add_rule(PolicyRule(
            name="security-profile-recommended",
            description="Security profile is recommended",
            check=lambda d: d.security is not None,
            severity="warning"
        ))
        
        return policy
    
    @staticmethod
    def permissive() -> "Policy":
        """Create a permissive policy that allows most tools."""
        policy = Policy(name="permissive")
        
        # Only warn, never reject
        policy.add_rule(PolicyRule(
            name="side-effects-info",
            description="Note: tool has side effects",
            check=lambda d: d.is_side_effect_free,
            severity="warning"
        ))
        
        return policy
    
    @staticmethod
    def gdpr() -> "Policy":
        """Create a GDPR-focused policy."""
        policy = Policy(name="gdpr")
        
        # Require EU data location if privacy profile present
        policy.add_rule(PolicyRule(
            name="eu-data-location",
            description="Data must be processed in EU",
            check=lambda d: (
                d.privacy is None or  # Allow if no privacy profile (graceful degradation)
                "EU" in d.privacy.data_location or
                "global" in d.privacy.data_location
            ),
            severity="error"
        ))
        
        # No persistent retention
        policy.add_rule(PolicyRule(
            name="no-persistent-retention",
            description="Tool must not persistently retain data",
            check=lambda d: d.constraints.data_retention != "persistent",
            severity="error"
        ))
        
        # Require encryption
        policy.add_rule(PolicyRule(
            name="require-encryption",
            description="Tool should use encryption",
            check=lambda d: (
                d.privacy is None or
                len(d.privacy.encryption) > 0
            ),
            severity="warning"
        ))
        
        # Prefer GDPR certified
        policy.add_rule(PolicyRule(
            name="gdpr-certified",
            description="GDPR certification preferred",
            check=lambda d: (
                d.compliance is not None and
                "GDPR" in d.compliance.standards
            ),
            severity="warning"
        ))
        
        return policy


@dataclass
class RuleResult:
    """Result of evaluating a single rule."""
    rule_name: str
    passed: bool
    severity: str
    message: str


@dataclass
class Decision:
    """Agent's decision about a tool."""
    tool_name: str
    decision: DecisionType
    reasoning: List[RuleResult]
    score: int = 100  # Base score, reduced by failures
    descriptor: Optional[UTCDDescriptor] = None
    
    @property
    def summary(self) -> str:
        """Get a human-readable summary of the decision."""
        status = "✓ APPROVED" if self.decision == DecisionType.APPROVED else "✗ REJECTED"
        if self.decision == DecisionType.WARNING:
            status = "⚠ APPROVED WITH WARNINGS"
        
        lines = [f"{status}: {self.tool_name} (score: {self.score}/100)"]
        
        for result in self.reasoning:
            icon = "✓" if result.passed else ("⚠" if result.severity == "warning" else "✗")
            lines.append(f"  {icon} {result.rule_name}: {result.message}")
        
        return "\n".join(lines)


class UTCDAgent:
    """Agent for reasoning over UTCD descriptors and making tool decisions."""
    
    def __init__(self, policy: Optional[Policy] = None):
        """Initialize agent with a policy."""
        self.policy = policy or Policy.standard()
        self.tools: List[UTCDDescriptor] = []
    
    def load_tool(self, descriptor: UTCDDescriptor) -> None:
        """Add a tool descriptor to the agent's knowledge."""
        self.tools.append(descriptor)
    
    def load_tools_from_directory(self, directory: str) -> int:
        """Load all tools from a directory. Returns count loaded."""
        descriptors = UTCDLoader.load_directory(directory)
        self.tools.extend(descriptors)
        return len(descriptors)
    
    def evaluate(self, descriptor: UTCDDescriptor) -> Decision:
        """Evaluate a single tool against the policy."""
        reasoning = []
        score = 100
        has_error = False
        has_warning = False
        
        for rule in self.policy.rules:
            passed = rule.evaluate(descriptor)
            
            if not passed:
                if rule.severity == "error":
                    has_error = True
                    score -= 50  # Major penalty
                else:
                    has_warning = True
                    score -= 10  # Minor penalty
            
            reasoning.append(RuleResult(
                rule_name=rule.name,
                passed=passed,
                severity=rule.severity,
                message=rule.description if passed else f"FAILED: {rule.description}"
            ))
        
        if has_error:
            decision_type = DecisionType.REJECTED
        elif has_warning:
            decision_type = DecisionType.WARNING
        else:
            decision_type = DecisionType.APPROVED
        
        return Decision(
            tool_name=descriptor.identity.name,
            decision=decision_type,
            reasoning=reasoning,
            score=max(0, score),
            descriptor=descriptor
        )
    
    def evaluate_all(self) -> List[Decision]:
        """Evaluate all loaded tools."""
        return [self.evaluate(tool) for tool in self.tools]
    
    def select_best(self, domain: Optional[str] = None) -> Optional[Decision]:
        """Select the best tool, optionally filtered by domain."""
        candidates = self.tools
        
        if domain:
            candidates = [t for t in candidates if t.capability.domain == domain]
        
        if not candidates:
            return None
        
        decisions = [self.evaluate(t) for t in candidates]
        
        # Filter to approved tools only
        approved = [d for d in decisions if d.decision != DecisionType.REJECTED]
        
        if not approved:
            # Flaw 4: Don't return rejected tools by default
            return None
        
        # Return highest scoring approved tool
        return max(approved, key=lambda d: d.score)
    
    def find_tools(
        self,
        domain: Optional[str] = None,
        max_side_effects: Optional[List[str]] = None,
        require_profiles: Optional[List[str]] = None,
        require_compliance: Optional[List[str]] = None
    ) -> List[Decision]:
        """Find tools matching specific criteria."""
        results = []
        
        for tool in self.tools:
            # Domain filter
            if domain and tool.capability.domain != domain:
                continue
            
            # Side effects filter
            if max_side_effects is not None:
                tool_effects = set(tool.constraints.side_effects)
                allowed = set(max_side_effects) | {"none"}
                if not tool_effects.issubset(allowed):
                    continue
            
            # Profile requirements
            if require_profiles:
                if not set(require_profiles).issubset(tool.profiles_present):
                    continue
            
            # Compliance requirements
            if require_compliance:
                if not tool.compliance:
                    continue
                if not set(require_compliance).issubset(set(tool.compliance.standards)):
                    continue
            
            results.append(self.evaluate(tool))
        
        # Sort by score
        return sorted(results, key=lambda d: d.score, reverse=True)
    
    def explain_rejection(self, descriptor: UTCDDescriptor) -> str:
        """Get a detailed explanation of why a tool would be rejected."""
        decision = self.evaluate(descriptor)
        
        if decision.decision == DecisionType.APPROVED:
            return f"Tool '{descriptor.identity.name}' would be APPROVED."
        
        lines = [f"Tool '{descriptor.identity.name}' is REJECTED for the following reasons:"]
        
        for result in decision.reasoning:
            if not result.passed and result.severity == "error":
                lines.append(f"  • {result.rule_name}: {result.message}")
        
        lines.append("")
        lines.append("To fix, the tool must:")
        
        for result in decision.reasoning:
            if not result.passed and result.severity == "error":
                lines.append(f"  • Satisfy: {result.rule_name}")
        
        return "\n".join(lines)
    
    def compare_tools(self, *tool_names: str) -> str:
        """Compare multiple tools and explain the differences."""
        tools_to_compare = []
        
        for name in tool_names:
            for tool in self.tools:
                if tool.identity.name == name:
                    tools_to_compare.append(tool)
                    break
        
        if len(tools_to_compare) < 2:
            return "Need at least 2 tools to compare."
        
        decisions = [self.evaluate(t) for t in tools_to_compare]
        
        lines = ["Tool Comparison:"]
        lines.append("-" * 60)
        
        for decision in sorted(decisions, key=lambda d: d.score, reverse=True):
            status = "✓" if decision.decision != DecisionType.REJECTED else "✗"
            lines.append(f"{status} {decision.tool_name}: score {decision.score}/100")
            lines.append(f"   Side effects: {decision.descriptor.constraints.side_effects}")
            lines.append(f"   Data retention: {decision.descriptor.constraints.data_retention}")
            lines.append(f"   Profiles: {decision.descriptor.profiles_present or 'none'}")
            lines.append("")
        
        best = max(decisions, key=lambda d: d.score)
        lines.append(f"Recommendation: {best.tool_name}")
        
        return "\n".join(lines)
