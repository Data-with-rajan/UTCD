"""
UTCD Validator - Validate UTCD descriptor files against schemas.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Union
from dataclasses import dataclass, field


# Try to import jsonschema, fall back to basic validation if not available
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
    severity: str = "error"  # "error" or "warning"


@dataclass
class ValidationResult:
    """Result of validating a UTCD descriptor."""
    valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    profiles_detected: Set[str] = field(default_factory=set)
    
    def __str__(self) -> str:
        if self.valid:
            profiles = ", ".join(self.profiles_detected) if self.profiles_detected else "none"
            return f"✓ Valid UTCD descriptor (profiles: {profiles})"
        else:
            error_msgs = [f"  - {e.path}: {e.message}" for e in self.errors]
            return f"✗ Invalid UTCD descriptor:\n" + "\n".join(error_msgs)


class UTCDValidator:
    """Validate UTCD descriptors against the schema."""
    
    # Profile detection keys
    PROFILE_KEYS = {
        "security": "security",
        "privacy": "privacy",
        "compliance": "compliance",
        "cost": "cost",
        "performance": "performance"
    }
    
    def __init__(self, schema_dir: Optional[Union[str, Path]] = None):
        """Initialize validator with optional schema directory."""
        if schema_dir:
            self.schema_dir = Path(schema_dir)
        else:
            # Automatically resolve the schema path relative to the package (Fix #1)
            self.schema_dir = Path(__file__).parent.parent / "schema"

        self.core_schema = None
        self.profile_schemas = {}
        
        # Ensure it loads even if instantiated with default args
        if self.schema_dir.exists() and HAS_JSONSCHEMA:
            self._load_schemas()
    
    def _load_schemas(self) -> None:
        """Load JSON schemas from disk."""
        core_path = self.schema_dir / "utcd-core.schema.json"
        if core_path.exists():
            with open(core_path, 'r') as f:
                self.core_schema = json.load(f)
        
        profiles_dir = self.schema_dir / "profiles"
        if profiles_dir.exists():
            for schema_file in profiles_dir.glob("*.schema.json"):
                profile_name = schema_file.stem.replace(".schema", "")
                with open(schema_file, 'r') as f:
                    self.profile_schemas[profile_name] = json.load(f)
    
    def validate(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate a UTCD descriptor dictionary."""
        errors = []
        warnings = []
        profiles_detected = set()
        
        # Validate core fields via Schema (Flaw 5: SSOT)
        if HAS_JSONSCHEMA and self.core_schema:
            validator = jsonschema.Draft202012Validator(self.core_schema)
            for error in validator.iter_errors(data):
                errors.append(ValidationError(
                    path=".".join([str(p) for p in error.path]),
                    message=error.message
                ))
        else:
            # Fallback validation: at least check critical nested fields (Fix #2)
            required = {
                "identity": ["name", "purpose"],
                "capability": ["domain", "inputs", "outputs"],
                "constraints": ["side_effects", "data_retention"]
            }
            for section, fields in required.items():
                if section not in data:
                    errors.append(ValidationError(path=section, message=f"Required top-level field '{section}' is missing"))
                    continue
                for f in fields:
                    if f not in data[section]:
                        errors.append(ValidationError(path=f"{section}.{f}", message=f"Missing required sub-field"))
        
        # Detect and validate profiles
        for profile_key, profile_name in self.PROFILE_KEYS.items():
            if profile_key in data:
                profiles_detected.add(profile_name)
                # Schema-based profile validation
                if HAS_JSONSCHEMA and profile_name in self.profile_schemas:
                    validator = jsonschema.Draft202012Validator(self.profile_schemas[profile_name])
                    for error in validator.iter_errors(data[profile_key]):
                        errors.append(ValidationError(
                            path=f"{profile_key}.{'.'.join([str(p) for p in error.path])}",
                            message=error.message
                        ))
        
        # Add warnings for missing recommended profiles
        if "security" not in profiles_detected:
            warnings.append(ValidationError(
                path="security",
                message="Security profile not present (recommended for trust verification)",
                severity="warning"
            ))
        
        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            profiles_detected=profiles_detected
        )
    
    def validate_file(self, path: Union[str, Path]) -> ValidationResult:
        """Validate a UTCD YAML file."""
        import yaml
        
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
    """CLI entry point for validation."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m utcd.validator <utcd_file.yaml>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    # Find schema directory relative to this file
    schema_dir = Path(__file__).parent.parent / "schema"
    
    validator = UTCDValidator(schema_dir=schema_dir if schema_dir.exists() else None)
    result = validator.validate_file(file_path)
    
    print(result)
    
    if result.warnings:
        print("\nWarnings:")
        for warning in result.warnings:
            print(f"  ⚠ {warning.path}: {warning.message}")
    
    sys.exit(0 if result.valid else 1)



if __name__ == "__main__":
    main()
