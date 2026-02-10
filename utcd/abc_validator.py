"""
ABC Validator - Validate Agent Behavior Contract (ABC) files.
"""

import json
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

# Try to import jsonschema
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


@dataclass
class ValidationError:
    """A single validation error."""
    path: str
    message: str
    severity: str = "error"


@dataclass
class ValidationResult:
    """Result of validating an ABC contract."""
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    
    def __str__(self) -> str:
        if self.valid:
            return "✓ Valid ABC Contract"
        else:
            error_msgs = [f"  - {e.path}: {e.message}" for e in self.errors]
            return "✗ Invalid ABC Contract:\n" + "\n".join(error_msgs)


class ABCValidator:
    """Validate ABC contracts against the schema and UTCD rules."""
    
    def __init__(self, schema_path: Optional[str | Path] = None):
        """Initialize validator with schema path."""
        self.schema_path = Path(schema_path) if schema_path else None
        self.schema = None
        
        if self.schema_path and self.schema_path.exists():
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate an ABC contract dictionary."""
        errors = []
        warnings = []
        
        if not HAS_JSONSCHEMA:
            # Fallback basic validation
            required_top = ["identity", "mission", "cognition", "tools", "execution", "risk", "ethics", "governance"]
            for field in required_top:
                if field not in data:
                    errors.append(ValidationError(path=field, message=f"Required top-level field '{field}' is missing"))
            
            return ValidationResult(valid=len(errors) == 0, errors=errors)

        try:
            jsonschema.validate(instance=data, schema=self.schema)
        except jsonschema.ValidationError as e:
            errors.append(ValidationError(
                path=".".join([str(p) for p in e.path]),
                message=e.message
            ))
        
        # Additional logic: Verify Risk Parity (Simple heuristic for v0.1)
        # e.g., if risk_level is low, but require_sandbox is true, maybe that's a warning?
        risk = data.get("risk", {})
        if risk.get("risk_level") == "low" and risk.get("require_sandbox") == True:
            warnings.append(ValidationError(
                path="risk.require_sandbox",
                message="Sandbox required for a low-risk agent; this is unusually restrictive but safe.",
                severity="warning"
            ))

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    def validate_file(self, path: str | Path) -> ValidationResult:
        """Validate an ABC YAML file."""
        path = Path(path)
        if not path.exists():
            return ValidationResult(
                valid=False,
                errors=[ValidationError(path=str(path), message="File not found")]
            )
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            return ValidationResult(
                valid=False,
                errors=[ValidationError(path=str(path), message=f"YAML parse error: {e}")]
            )
        
        return self.validate(data)


def main():
    """CLI entry point."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="ABC Validator CLI")
    parser.add_argument("contract", help="Path to the .abc.yaml file")
    parser.add_argument("--schema", help="Path to abc-schema.json")
    
    args = parser.parse_args()
    
    # Resolve schema path
    schema_path = args.schema
    if not schema_path:
        # Default relative to this tool
        schema_path = Path(__file__).parent.parent / "abc" / "abc-schema.json"
    
    validator = ABCValidator(schema_path=schema_path)
    result = validator.validate_file(args.contract)
    
    print(result)
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠ {warning.path}: {warning.message}")
    
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
