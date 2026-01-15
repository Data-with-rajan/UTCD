#!/usr/bin/env python3
"""
Tests for UTCD Validator
"""

import pytest
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utcd.validator import UTCDValidator, ValidationResult


class TestValidator:
    """Tests for UTCD Validator."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = UTCDValidator()
    
    def test_valid_minimal_descriptor(self):
        """Test validation of a minimal valid descriptor."""
        data = {
            "utcd_version": "1.0",
            "identity": {
                "name": "Test Tool",
                "purpose": "A test tool"
            },
            "capability": {
                "domain": "testing",
                "inputs": ["input1"],
                "outputs": ["output1"]
            },
            "constraints": {
                "side_effects": ["none"],
                "data_retention": "none"
            },
            "connection": {
                "modes": [
                    {"type": "cli", "detail": "test-cli"}
                ]
            }
        }
        
        result = self.validator.validate(data)
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_missing_required_field(self):
        """Test that missing required fields are detected."""
        data = {
            "utcd_version": "1.0",
            "identity": {
                "name": "Test Tool"
                # Missing "purpose"
            },
            "capability": {
                "domain": "testing",
                "inputs": [],
                "outputs": []
            },
            "constraints": {
                "side_effects": ["none"],
                "data_retention": "none"
            },
            "connection": {
                "modes": [{"type": "cli", "detail": "test"}]
            }
        }
        
        result = self.validator.validate(data)
        assert result.valid is False
        assert any("purpose" in e.path for e in result.errors)
    
    def test_invalid_data_retention(self):
        """Test that invalid data_retention values are rejected."""
        data = {
            "utcd_version": "1.0",
            "identity": {"name": "Test", "purpose": "Test"},
            "capability": {"domain": "test", "inputs": [], "outputs": []},
            "constraints": {
                "side_effects": ["none"],
                "data_retention": "invalid_value"  # Invalid
            },
            "connection": {"modes": [{"type": "cli", "detail": "test"}]}
        }
        
        result = self.validator.validate(data)
        assert result.valid is False
        assert any("data_retention" in e.path for e in result.errors)
    
    def test_empty_side_effects(self):
        """Test that empty side_effects array is rejected."""
        data = {
            "utcd_version": "1.0",
            "identity": {"name": "Test", "purpose": "Test"},
            "capability": {"domain": "test", "inputs": [], "outputs": []},
            "constraints": {
                "side_effects": [],  # Empty - invalid
                "data_retention": "none"
            },
            "connection": {"modes": [{"type": "cli", "detail": "test"}]}
        }
        
        result = self.validator.validate(data)
        assert result.valid is False
    
    def test_profile_detection(self):
        """Test that profiles are correctly detected."""
        data = {
            "utcd_version": "1.0",
            "identity": {"name": "Test", "purpose": "Test"},
            "capability": {"domain": "test", "inputs": [], "outputs": []},
            "constraints": {"side_effects": ["none"], "data_retention": "none"},
            "connection": {"modes": [{"type": "cli", "detail": "test"}]},
            "security": {
                "publisher": "did:web:example.com"
            },
            "privacy": {
                "data_location": ["EU"]
            }
        }
        
        result = self.validator.validate(data)
        assert "security" in result.profiles_detected
        assert "privacy" in result.profiles_detected
    
    def test_missing_security_warning(self):
        """Test that missing security profile generates warning."""
        data = {
            "utcd_version": "1.0",
            "identity": {"name": "Test", "purpose": "Test"},
            "capability": {"domain": "test", "inputs": [], "outputs": []},
            "constraints": {"side_effects": ["none"], "data_retention": "none"},
            "connection": {"modes": [{"type": "cli", "detail": "test"}]}
        }
        
        result = self.validator.validate(data)
        assert result.valid is True  # Still valid
        assert len(result.warnings) > 0  # But has warnings
        assert any("security" in w.path.lower() for w in result.warnings)


class TestValidatorWithFiles:
    """Tests for UTCD Validator with example files."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = UTCDValidator()
        self.examples_dir = Path(__file__).parent.parent / "examples"
    
    def test_validate_csv_analyzer(self):
        """Test validation of csv-analyzer example."""
        result = self.validator.validate_file(
            self.examples_dir / "csv-analyzer.utcd.yaml"
        )
        assert result.valid is True
        assert "security" in result.profiles_detected
        assert "privacy" in result.profiles_detected
        assert "cost" in result.profiles_detected
    
    def test_validate_file_reader(self):
        """Test validation of file-reader example."""
        result = self.validator.validate_file(
            self.examples_dir / "file-reader.utcd.yaml"
        )
        assert result.valid is True
    
    def test_validate_email_sender(self):
        """Test validation of email-sender example."""
        result = self.validator.validate_file(
            self.examples_dir / "email-sender.utcd.yaml"
        )
        assert result.valid is True
    
    def test_validate_nonexistent_file(self):
        """Test validation of nonexistent file."""
        result = self.validator.validate_file("nonexistent.yaml")
        assert result.valid is False
        assert any("not found" in e.message.lower() for e in result.errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
