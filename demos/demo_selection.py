#!/usr/bin/env python3
"""
Demo: Tool Selection

This demo shows how the UTCD agent selects the best tool
from multiple candidates based on policy evaluation.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utcd import UTCDAgent, UTCDLoader, Policy


def main():
    print("=" * 60)
    print("UTCD Demo: Tool Selection")
    print("=" * 60)
    print()
    
    # Create agent with standard policy
    agent = UTCDAgent(policy=Policy.standard())
    
    # Load example tools
    examples_dir = Path(__file__).parent.parent / "examples"
    count = agent.load_tools_from_directory(examples_dir)
    print(f"Loaded {count} tools from {examples_dir}")
    print()
    
    # List all tools
    print("Available tools:")
    for tool in agent.tools:
        print(f"  - {tool.identity.name} ({tool.capability.domain})")
        print(f"    Side effects: {tool.constraints.side_effects}")
        print(f"    Data retention: {tool.constraints.data_retention}")
        print()
    
    # Scenario 1: Find best data processing tool
    print("-" * 60)
    print("Scenario 1: Select best data processing tool")
    print("-" * 60)
    
    results = agent.find_tools(domain="data-processing")
    
    if results:
        print(f"\nFound {len(results)} candidates:")
        for decision in results:
            print(f"\n{decision.summary}")
        
        best = results[0]
        print(f"\n✓ Selected: {best.tool_name} (score: {best.score}/100)")
    else:
        print("No matching tools found.")
    
    print()
    
    # Scenario 2: Find safest communication tool
    print("-" * 60)
    print("Scenario 2: Select safest communication tool")
    print("-" * 60)
    
    results = agent.find_tools(domain="communication")
    
    if results:
        for decision in results:
            print(f"\n{decision.summary}")
    else:
        print("No matching tools found.")
    
    print()
    
    # Scenario 3: Compare all tools
    print("-" * 60)
    print("Scenario 3: Evaluate all tools")
    print("-" * 60)
    
    all_decisions = agent.evaluate_all()
    
    # Sort by score
    all_decisions.sort(key=lambda d: d.score, reverse=True)
    
    print("\nRanking (by safety score):")
    for i, decision in enumerate(all_decisions, 1):
        status = "✓" if decision.decision.value == "approved" else "⚠" if decision.decision.value == "warning" else "✗"
        print(f"  {i}. {status} {decision.tool_name}: {decision.score}/100")
    
    print()
    print("=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
