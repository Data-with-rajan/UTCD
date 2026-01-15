#!/usr/bin/env python3
"""
Demo: Tool Rejection

This demo shows how the UTCD agent rejects unsafe tools
and provides clear explanations for the rejection.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utcd import UTCDAgent, UTCDLoader, Policy


def main():
    print("=" * 60)
    print("UTCD Demo: Tool Rejection")
    print("=" * 60)
    print()
    
    # Load the unsafe executor tool
    examples_dir = Path(__file__).parent.parent / "examples"
    unsafe_tool = UTCDLoader.load(examples_dir / "unsafe-executor.utcd.yaml")
    
    print(f"Tool: {unsafe_tool.identity.name}")
    print(f"Purpose: {unsafe_tool.identity.purpose}")
    print(f"Side effects: {unsafe_tool.constraints.side_effects}")
    print(f"Data retention: {unsafe_tool.constraints.data_retention}")
    print()
    
    # Test with different policies
    policies = [
        ("Strict Policy", Policy.strict()),
        ("Standard Policy", Policy.standard()),
        ("Permissive Policy", Policy.permissive()),
        ("GDPR Policy", Policy.gdpr()),
    ]
    
    for policy_name, policy in policies:
        print("-" * 60)
        print(f"Testing with: {policy_name}")
        print("-" * 60)
        
        agent = UTCDAgent(policy=policy)
        decision = agent.evaluate(unsafe_tool)
        
        print(f"\nDecision: {decision.decision.value.upper()}")
        print(f"Score: {decision.score}/100")
        print()
        print("Rule evaluations:")
        for result in decision.reasoning:
            icon = "✓" if result.passed else "✗"
            print(f"  {icon} [{result.severity}] {result.rule_name}")
            if not result.passed:
                print(f"      → {result.message}")
        print()
    
    # Detailed rejection explanation
    print("=" * 60)
    print("Detailed Rejection Explanation (Strict Policy)")
    print("=" * 60)
    
    agent = UTCDAgent(policy=Policy.strict())
    explanation = agent.explain_rejection(unsafe_tool)
    print()
    print(explanation)
    
    print()
    print("=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
