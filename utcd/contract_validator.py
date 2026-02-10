"""
Contract Validator - Validate Agent Behavior Contract files.
"""

import json
import yaml
from pathlib import Path
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass, field

# Try to import jsonschema
try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


from .loader import UTCDLoader, UTCDDescriptor

@dataclass
class ValidationError:
    """A single validation error."""
    path: str
    message: str
    severity: str = "error"


@dataclass
class ValidationResult:
    """Result of validating a contract."""
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    
    def __str__(self) -> str:
        if self.valid:
            return "✓ Valid Agent Behavior Contract"
        else:
            error_msgs = [f"  - {e.path}: {e.message}" for e in self.errors]
            return "✗ Invalid Agent Behavior Contract:\n" + "\n".join(error_msgs)


class ContractValidator:
    """Validate behavior contracts against the schema and UTCD rules."""
    
    RISK_LEVELS = {"low": 1, "medium": 2, "high": 3}
    
    def __init__(self, schema_path: Optional[Union[str, Path]] = None, utcd_dir: Optional[Union[str, Path]] = None):
        """Initialize validator with schema and optional tool directory."""
        self.schema_path = Path(schema_path) if schema_path else None
        self.utcd_dir = Path(utcd_dir) if utcd_dir else None
        self.schema = None
        
        if self.schema_path and self.schema_path.exists():
            with open(self.schema_path, 'r') as f:
                self.schema = json.load(f)
    
    def _calculate_tool_risk(self, tool: UTCDDescriptor) -> str:
        """Heuristic to determine tool risk level (Flaw 2)."""
        side_effects = set(tool.constraints.side_effects)
        retention = tool.constraints.data_retention
        
        # High Risk indicators
        high_risk_triggers = {"process:spawn", "net:arbitrary", "io:filesystem-write"}
        if any(trigger in side_effects for trigger in high_risk_triggers) or retention == "persistent":
            return "high"
            
        # Medium Risk indicators
        medium_risk_triggers = {"net:http-outbound", "io:filesystem-read"}
        if any(trigger in side_effects for trigger in medium_risk_triggers) or retention == "session":
            return "medium"
            
        return "low"

    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a contract dictionary."""
        errors = []
        warnings = []
        
        if not HAS_JSONSCHEMA:
            # Fallback basic validation
            required_top = ["identity", "mission", "cognition", "tools", "execution", "risk", "ethics", "governance"]
            for field in required_top:
                if field not in data:
                    errors.append(ValidationError(path=field, message=f"Required top-level field '{field}' is missing"))
            
            return ValidationResult(valid=len(errors) == 0, errors=errors)

        # Multi-error validation (Flaw 3)
        validator = jsonschema.Draft202012Validator(self.schema)
        for error in validator.iter_errors(data):
            errors.append(ValidationError(
                path=".".join([str(p) for p in error.path]),
                message=error.message
            ))
        
        # Stop early if basic structure is wrong
        if errors:
            return ValidationResult(valid=False, errors=errors)

        # Flaw 2: Real Risk Inheritance
        contract_risk_str = data.get("risk", {}).get("risk_level", "low")
        contract_risk = self.RISK_LEVELS.get(contract_risk_str, 1)
        
        allowed_tools = data.get("tools", {}).get("allowed_tools", [])
        if self.utcd_dir and self.utcd_dir.exists():
            loader = UTCDLoader()
            for tool_ref in allowed_tools:
                # Resolve tool reference (utcd:tool-name:v1 -> tool-name.utcd.yaml)
                if tool_ref.startswith("utcd:"):
                    tool_name = tool_ref.split(":")[1]
                    tool_path = self.utcd_dir / f"{tool_name}.utcd.yaml"
                    
                    if tool_path.exists():
                        try:
                            tool_desc = loader.load(tool_path)
                            tool_risk_str = self._calculate_tool_risk(tool_desc)
                            tool_risk_val = self.RISK_LEVELS.get(tool_risk_str, 1)
                            
                            if tool_risk_val > contract_risk:
                                errors.append(ValidationError(
                                    path=f"tools.allowed_tools",
                                    message=f"Risk Mismatch: Tool '{tool_name}' has '{tool_risk_str}' risk, but contract is '{contract_risk_str}'."
                                ))
                        except Exception as e:
                            warnings.append(ValidationError(
                                path=f"tools.allowed_tools",
                                message=f"Could not load tool {tool_name} for risk check: {e}",
                                severity="warning"
                            ))
                    else:
                        warnings.append(ValidationError(
                            path=f"tools.allowed_tools",
                            message=f"Tool reference {tool_ref} not found in {self.utcd_dir}. Risk inheritance not verified.",
                            severity="warning"
                        ))

        # Additional logic: Verify Risk Parity
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

    def validate_file(self, path: Union[str, Path]) -> ValidationResult:
        """Validate a contract YAML file."""
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
    
    parser = argparse.ArgumentParser(description="Contract Validator CLI")
    parser.add_argument("contract", help="Path to the .contract.yaml file")
    parser.add_argument("--schema", help="Path to contract-schema.json")
    
    args = parser.parse_args()
    
    # Resolve paths
    schema_path = args.schema
    if not schema_path:
        schema_path = Path(__file__).parent.parent / "contracts" / "contract-schema.json"
    
    utcd_dir = Path(__file__).parent.parent / "examples"
    
    validator = ContractValidator(schema_path=schema_path, utcd_dir=utcd_dir)
    result = validator.validate_file(args.contract)
    
    print(result)
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠ {warning.path}: {warning.message}")
    
    sys.exit(0 if result.valid else 1)


if __name__ == "__main__":
    main()
