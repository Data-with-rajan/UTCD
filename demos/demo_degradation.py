#!/usr/bin/env python3
"""
Demo: Graceful Degradation

This demo shows how the UTCD agent handles tools that are
missing optional profiles, demonstrating graceful degradation.
"""

import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utcd import UTCDAgent, UTCDLoader, Policy


def main():
    print("=" * 60)
    print("UTCD Demo: Graceful Degradation")
    print("=" * 60)
    print()
    
    # Load tools with varying profile completeness
    examples_dir = Path(__file__).parent.parent / "examples"
    
    tools = [
        ("Full Profiles", UTCDLoader.load(examples_dir / "csv-analyzer.utcd.yaml")),
        ("Minimal Profiles", UTCDLoader.load(examples_dir / "file-reader.utcd.yaml")),
        ("Some Profiles", UTCDLoader.load(examples_dir / "email-sender.utcd.yaml")),
        ("No Profiles", UTCDLoader.load(examples_dir / "unsafe-executor.utcd.yaml")),
    ]
    
    # Show profile completeness for each tool
    print("Profile completeness:")
    print("-" * 60)
    for name, tool in tools:
        profiles = tool.profiles_present
        print(f"\n{tool.identity.name}:")
        print(f"  Profiles present: {profiles if profiles else 'none'}")
        print(f"  Has signatures: {tool.has_signatures}")
        print(f"  Is side-effect free: {tool.is_side_effect_free}")
    
    print()
    print("=" * 60)
    print("GDPR Policy Evaluation (with graceful degradation)")
    print("=" * 60)
    
    agent = UTCDAgent(policy=Policy.gdpr())
    
    for name, tool in tools:
        agent.load_tool(tool)
    
    print("\nKey insight: GDPR policy allows tools WITHOUT privacy profiles")
    print("(graceful degradation), but rejects tools that HAVE privacy")
    print("profiles with non-EU data location.")
    print()
    
    for name, tool in tools:
        decision = agent.evaluate(tool)
        
        print(f"\n{tool.identity.name}:")
        print(f"  Decision: {decision.decision.value.upper()}")
        print(f"  Score: {decision.score}/100")
        
        # Show relevant details
        if tool.privacy:
            print(f"  Data location: {tool.privacy.data_location}")
        else:
            print(f"  Data location: (no privacy profile - allowed)")
        
        if tool.compliance:
            print(f"  Compliance: {tool.compliance.standards}")
        else:
            print(f"  Compliance: (no compliance profile)")
    
    print()
    
    # Demonstrate finding tools with optional requirements
    print("=" * 60)
    print("Finding Tools with Specific Requirements")
    print("=" * 60)
    
    print("\n1. Tools with security profile:")
    results = agent.find_tools(require_profiles=["security"])
    for r in results:
        print(f"   - {r.tool_name} (score: {r.score})")
    
    print("\n2. Tools with GDPR compliance:")
    results = agent.find_tools(require_compliance=["GDPR"])
    for r in results:
        print(f"   - {r.tool_name} (score: {r.score})")
    
    print("\n3. Tools with no side effects:")
    results = agent.find_tools(max_side_effects=["none"])
    for r in results:
        print(f"   - {r.tool_name} (score: {r.score})")
    
    print()
    print("=" * 60)
    print("Demo complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
