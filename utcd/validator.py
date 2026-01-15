"""
UTCD Validator - Validate UTCD descriptor files against schemas.
"""

import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Set
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
    
    # Required core fields
    REQUIRED_CORE_FIELDS = ["utcd_version", "identity", "capability", "constraints", "connection"]
    REQUIRED_IDENTITY_FIELDS = ["name", "purpose"]
    REQUIRED_CAPABILITY_FIELDS = ["domain", "inputs", "outputs"]
    REQUIRED_CONSTRAINTS_FIELDS = ["side_effects", "data_retention"]
    REQUIRED_CONNECTION_FIELDS = ["modes"]
    
    # Valid values
    VALID_DATA_RETENTION = ["none", "session", "persistent"]
    VALID_ENCRYPTION = ["in-transit", "at-rest", "end-to-end", "none"]
    VALID_PII_HANDLING = ["none", "anonymized", "pseudonymized", "stored"]
    VALID_DATA_DELETION = ["immediate", "on-request", "scheduled", "never"]
    VALID_COST_MODELS = ["free", "pay-per-call", "subscription", "usage-based", "enterprise"]
    
    # Profile detection keys
    PROFILE_KEYS = {
        "security": "security",
        "privacy": "privacy",
        "compliance": "compliance",
        "cost": "cost",
        "performance": "performance"
    }
    
    def __init__(self, schema_dir: Optional[str | Path] = None):
        """Initialize validator with optional schema directory."""
        self.schema_dir = Path(schema_dir) if schema_dir else None
        self.core_schema = None
        self.profile_schemas = {}
        
        if self.schema_dir and HAS_JSONSCHEMA:
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
        
        # Validate core fields
        core_errors = self._validate_core(data)
        errors.extend(core_errors)
        
        # Detect and validate profiles
        for profile_key, profile_name in self.PROFILE_KEYS.items():
            if profile_key in data:
                profiles_detected.add(profile_name)
                profile_errors = self._validate_profile(profile_name, data[profile_key])
                errors.extend(profile_errors)
        
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
    
    def validate_file(self, path: str | Path) -> ValidationResult:
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
    
    def _validate_core(self, data: Dict[str, Any]) -> List[ValidationError]:
        """Validate core UTCD fields."""
        errors = []
        
        # Check required top-level fields
        for field in self.REQUIRED_CORE_FIELDS:
            if field not in data:
                errors.append(ValidationError(
                    path=field,
                    message=f"Required field '{field}' is missing"
                ))
        
        # Validate utcd_version
        if "utcd_version" in data:
            version = data["utcd_version"]
            if not isinstance(version, str):
                errors.append(ValidationError(
                    path="utcd_version",
                    message="utcd_version must be a string"
                ))
        
        # Validate identity
        if "identity" in data:
            identity = data["identity"]
            if not isinstance(identity, dict):
                errors.append(ValidationError(
                    path="identity",
                    message="identity must be an object"
                ))
            else:
                for field in self.REQUIRED_IDENTITY_FIELDS:
                    if field not in identity:
                        errors.append(ValidationError(
                            path=f"identity.{field}",
                            message=f"Required field 'identity.{field}' is missing"
                        ))
        
        # Validate capability
        if "capability" in data:
            capability = data["capability"]
            if not isinstance(capability, dict):
                errors.append(ValidationError(
                    path="capability",
                    message="capability must be an object"
                ))
            else:
                for field in self.REQUIRED_CAPABILITY_FIELDS:
                    if field not in capability:
                        errors.append(ValidationError(
                            path=f"capability.{field}",
                            message=f"Required field 'capability.{field}' is missing"
                        ))
                
                # Validate inputs/outputs are arrays
                for field in ["inputs", "outputs"]:
                    if field in capability and not isinstance(capability[field], list):
                        errors.append(ValidationError(
                            path=f"capability.{field}",
                            message=f"capability.{field} must be an array"
                        ))
        
        # Validate constraints
        if "constraints" in data:
            constraints = data["constraints"]
            if not isinstance(constraints, dict):
                errors.append(ValidationError(
                    path="constraints",
                    message="constraints must be an object"
                ))
            else:
                for field in self.REQUIRED_CONSTRAINTS_FIELDS:
                    if field not in constraints:
                        errors.append(ValidationError(
                            path=f"constraints.{field}",
                            message=f"Required field 'constraints.{field}' is missing"
                        ))
                
                # Validate side_effects is array
                if "side_effects" in constraints:
                    if not isinstance(constraints["side_effects"], list):
                        errors.append(ValidationError(
                            path="constraints.side_effects",
                            message="constraints.side_effects must be an array"
                        ))
                    elif len(constraints["side_effects"]) == 0:
                        errors.append(ValidationError(
                            path="constraints.side_effects",
                            message="constraints.side_effects must have at least one value"
                        ))
                
                # Validate data_retention enum
                if "data_retention" in constraints:
                    if constraints["data_retention"] not in self.VALID_DATA_RETENTION:
                        errors.append(ValidationError(
                            path="constraints.data_retention",
                            message=f"constraints.data_retention must be one of: {self.VALID_DATA_RETENTION}"
                        ))
        
        # Validate connection
        if "connection" in data:
            connection = data["connection"]
            if not isinstance(connection, dict):
                errors.append(ValidationError(
                    path="connection",
                    message="connection must be an object"
                ))
            else:
                if "modes" not in connection:
                    errors.append(ValidationError(
                        path="connection.modes",
                        message="Required field 'connection.modes' is missing"
                    ))
                elif not isinstance(connection["modes"], list):
                    errors.append(ValidationError(
                        path="connection.modes",
                        message="connection.modes must be an array"
                    ))
                elif len(connection["modes"]) == 0:
                    errors.append(ValidationError(
                        path="connection.modes",
                        message="connection.modes must have at least one mode"
                    ))
                else:
                    for i, mode in enumerate(connection["modes"]):
                        if not isinstance(mode, dict):
                            errors.append(ValidationError(
                                path=f"connection.modes[{i}]",
                                message="Each mode must be an object"
                            ))
                        else:
                            if "type" not in mode:
                                errors.append(ValidationError(
                                    path=f"connection.modes[{i}].type",
                                    message="Each mode must have a 'type' field"
                                ))
                            if "detail" not in mode:
                                errors.append(ValidationError(
                                    path=f"connection.modes[{i}].detail",
                                    message="Each mode must have a 'detail' field"
                                ))
        
        return errors
    
    def _validate_profile(self, profile_name: str, data: Any) -> List[ValidationError]:
        """Validate a specific profile."""
        errors = []
        
        if not isinstance(data, dict):
            errors.append(ValidationError(
                path=profile_name,
                message=f"{profile_name} must be an object"
            ))
            return errors
        
        # Profile-specific validation
        if profile_name == "privacy":
            if "encryption" in data:
                for enc in data["encryption"]:
                    if enc not in self.VALID_ENCRYPTION:
                        errors.append(ValidationError(
                            path=f"{profile_name}.encryption",
                            message=f"Invalid encryption value: {enc}. Must be one of: {self.VALID_ENCRYPTION}"
                        ))
            
            if "pii_handling" in data:
                if data["pii_handling"] not in self.VALID_PII_HANDLING:
                    errors.append(ValidationError(
                        path=f"{profile_name}.pii_handling",
                        message=f"Invalid pii_handling value. Must be one of: {self.VALID_PII_HANDLING}"
                    ))
        
        elif profile_name == "cost":
            if "model" in data:
                if data["model"] not in self.VALID_COST_MODELS:
                    errors.append(ValidationError(
                        path=f"{profile_name}.model",
                        message=f"Invalid cost model. Must be one of: {self.VALID_COST_MODELS}"
                    ))
        
        return errors


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
