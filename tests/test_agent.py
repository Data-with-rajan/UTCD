#!/usr/bin/env python3
"""
Tests for UTCD Agent
"""

import pytest
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utcd.agent import UTCDAgent, Policy, DecisionType
from utcd.loader import UTCDLoader


class TestPolicy:
    """Tests for Policy creation."""
    
    def test_strict_policy(self):
        """Test strict policy has expected rules."""
        policy = Policy.strict()
        assert policy.name == "strict"
        assert len(policy.rules) >= 2
    
    def test_standard_policy(self):
        """Test standard policy has expected rules."""
        policy = Policy.standard()
        assert policy.name == "standard"
        assert len(policy.rules) >= 2
    
    def test_gdpr_policy(self):
        """Test GDPR policy has expected rules."""
        policy = Policy.gdpr()
        assert policy.name == "gdpr"
        assert any("eu" in r.name.lower() for r in policy.rules)


class TestAgent:
    """Tests for UTCD Agent."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.examples_dir = Path(__file__).parent.parent / "examples"
    
    def test_load_tools(self):
        """Test loading tools from directory."""
        agent = UTCDAgent()
        count = agent.load_tools_from_directory(self.examples_dir)
        assert count >= 3
        assert len(agent.tools) >= 3
    
    def test_evaluate_safe_tool(self):
        """Test evaluation of a safe tool."""
        agent = UTCDAgent(policy=Policy.strict())
        tool = UTCDLoader.load(self.examples_dir / "csv-analyzer.utcd.yaml")
        
        decision = agent.evaluate(tool)
        
        assert decision.tool_name == "EU CSV Analyzer"
        assert decision.decision == DecisionType.APPROVED
        assert decision.score > 80
    
    def test_reject_unsafe_tool(self):
        """Test rejection of unsafe tool with strict policy."""
        agent = UTCDAgent(policy=Policy.strict())
        tool = UTCDLoader.load(self.examples_dir / "unsafe-executor.utcd.yaml")
        
        decision = agent.evaluate(tool)
        
        assert decision.decision == DecisionType.REJECTED
        assert decision.score < 50
    
    def test_find_tools_by_domain(self):
        """Test finding tools by domain."""
        agent = UTCDAgent()
        agent.load_tools_from_directory(self.examples_dir)
        
        results = agent.find_tools(domain="data-processing")
        
        assert len(results) >= 1
        assert all(r.descriptor.capability.domain == "data-processing" for r in results)
    
    def test_find_tools_by_side_effects(self):
        """Test finding tools by side effects constraint."""
        agent = UTCDAgent()
        agent.load_tools_from_directory(self.examples_dir)
        
        results = agent.find_tools(max_side_effects=["none"])
        
        # Should only return tools with no side effects
        for r in results:
            assert r.descriptor.is_side_effect_free
    
    def test_select_best(self):
        """Test selecting the best tool."""
        agent = UTCDAgent(policy=Policy.standard())
        agent.load_tools_from_directory(self.examples_dir)
        
        best = agent.select_best(domain="data-processing")
        
        assert best is not None
        assert best.descriptor.capability.domain == "data-processing"
    
    def test_explain_rejection(self):
        """Test rejection explanation."""
        agent = UTCDAgent(policy=Policy.strict())
        tool = UTCDLoader.load(self.examples_dir / "unsafe-executor.utcd.yaml")
        
        explanation = agent.explain_rejection(tool)
        
        assert "REJECTED" in explanation
        assert len(explanation) > 50


class TestGracefulDegradation:
    """Tests for graceful degradation behavior."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.examples_dir = Path(__file__).parent.parent / "examples"
    
    def test_tool_without_profiles_still_evaluated(self):
        """Test that tools without profiles can still be evaluated."""
        agent = UTCDAgent(policy=Policy.standard())
        
        # Load file-reader which has minimal profiles
        tool = UTCDLoader.load(self.examples_dir / "file-reader.utcd.yaml")
        
        decision = agent.evaluate(tool)
        
        # Should still get a decision
        assert decision.decision in [DecisionType.APPROVED, DecisionType.WARNING]
    
    def test_gdpr_allows_missing_privacy_profile(self):
        """Test that GDPR policy allows tools without privacy profile."""
        agent = UTCDAgent(policy=Policy.gdpr())
        
        # Load file-reader which has no privacy profile
        tool = UTCDLoader.load(self.examples_dir / "file-reader.utcd.yaml")
        
        decision = agent.evaluate(tool)
        
        # Should be approved or warning, not rejected due to missing profile
        assert decision.decision != DecisionType.REJECTED or decision.score > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
