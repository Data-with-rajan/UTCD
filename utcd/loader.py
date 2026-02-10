"""
UTCD Loader - Load and parse UTCD descriptor files.
"""

import yaml
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Set, Union
from dataclasses import dataclass, field

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    from cryptography.exceptions import InvalidSignature
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False


@dataclass
class ConnectionMode:
    """A connection mode for a tool."""
    type: str
    detail: str


@dataclass
class Identity:
    """Tool identity information."""
    name: str
    purpose: str


@dataclass
class Capability:
    """Tool capability information."""
    domain: str
    inputs: List[str]
    outputs: List[str]


@dataclass
class Constraints:
    """Tool constraints."""
    side_effects: List[str]
    data_retention: str


@dataclass
class Connection:
    """Tool connection information."""
    modes: List[ConnectionMode]


@dataclass
class SecurityProfile:
    """Optional security profile."""
    fingerprint: Optional[str] = None
    publisher: Optional[str] = None
    signatures: List[Dict[str, str]] = field(default_factory=list)
    audit_url: Optional[str] = None
    vulnerability_disclosure: Optional[str] = None


@dataclass
class PrivacyProfile:
    """Optional privacy profile."""
    data_location: List[str] = field(default_factory=list)
    encryption: List[str] = field(default_factory=list)
    pii_handling: Optional[str] = None
    data_deletion: Optional[str] = None


@dataclass
class ComplianceInfo:
    """Compliance information."""
    standards: List[str] = field(default_factory=list)
    certifications: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class CostEstimate:
    """Cost estimate for a usage pattern."""
    input: str
    cost: str
    latency_p50: Optional[str] = None
    latency_p99: Optional[str] = None


@dataclass
class CostProfile:
    """Optional cost profile."""
    model: Optional[str] = None
    currency: str = "USD"
    estimates: List[CostEstimate] = field(default_factory=list)
    free_tier: Optional[Dict[str, Any]] = None


@dataclass
class PerformanceInfo:
    """Performance characteristics."""
    availability: Optional[str] = None
    rate_limit: Optional[str] = None
    max_payload: Optional[str] = None


@dataclass
class UTCDDescriptor:
    """Complete UTCD descriptor with core and optional profiles."""
    
    # Core (required)
    utcd_version: str
    identity: Identity
    capability: Capability
    constraints: Constraints
    connection: Connection
    
    # Profiles (optional)
    security: Optional[SecurityProfile] = None
    privacy: Optional[PrivacyProfile] = None
    compliance: Optional[ComplianceInfo] = None
    cost: Optional[CostProfile] = None
    performance: Optional[PerformanceInfo] = None
    
    # Source tracking
    source_path: Optional[str] = None
    
    @property
    def profiles_present(self) -> Set[str]:
        """Return set of profile names that are present."""
        profiles = set()
        if self.security:
            profiles.add("security")
        if self.privacy:
            profiles.add("privacy")
        if self.compliance:
            profiles.add("compliance")
        if self.cost:
            profiles.add("cost")
        if self.performance:
            profiles.add("performance")
        return profiles
    
    @property
    def has_signatures(self) -> bool:
        """Check if tool has cryptographic signatures."""
        return self.security is not None and len(self.security.signatures) > 0
    
    @property
    def is_side_effect_free(self) -> bool:
        """Check if tool has no side effects."""
        return self.constraints.side_effects == ["none"]
    
    @property
    def retains_data(self) -> bool:
        """Check if tool retains data."""
        return self.constraints.data_retention != "none"
    
    def verify_signatures(self) -> bool:
        """
        Verify all cryptographic signatures in the security profile.
        Returns True if all signatures are valid, False otherwise.
        """
        if not self.has_signatures:
            return True  # Vacuously true if no signatures present (but check has_signatures elsewhere)
            
        if not HAS_CRYPTOGRAPHY:
            print("Warning: cryptography library not installed. Skipping signature verification.")
            return False

        # In a real implementation, we would canonicalize the descriptor data
        # For this version, we verify signatures over the tool's identity name + purpose
        message = f"{self.identity.name}:{self.identity.purpose}".encode('utf-8')
        
        try:
            for sig_data in self.security.signatures:
                public_key_hex = sig_data.get("public_key")
                signature_hex = sig_data.get("signature")
                
                if not public_key_hex or not signature_hex:
                    return False
                
                public_key = ed25519.Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
                public_key.verify(bytes.fromhex(signature_hex), message)
            
            return True
        except (InvalidSignature, ValueError, TypeError) as e:
            print(f"Signature verification failed: {e}")
            return False


class UTCDLoader:
    """Load UTCD descriptors from files."""
    
    @staticmethod
    def load(path: Union[str, Path]) -> UTCDDescriptor:
        """Load a UTCD descriptor from a YAML file."""
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"UTCD file not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return UTCDLoader.parse(data, source_path=str(path))
    
    @staticmethod
    def parse(data: Dict[str, Any], source_path: Optional[str] = None) -> UTCDDescriptor:
        """Parse a UTCD descriptor from a dictionary."""
        
        # Parse core identity
        identity_data = data.get("identity", {})
        identity = Identity(
            name=identity_data.get("name", ""),
            purpose=identity_data.get("purpose", "")
        )
        
        # Parse capability
        cap_data = data.get("capability", {})
        capability = Capability(
            domain=cap_data.get("domain", ""),
            inputs=cap_data.get("inputs", []),
            outputs=cap_data.get("outputs", [])
        )
        
        # Parse constraints
        const_data = data.get("constraints", {})
        constraints = Constraints(
            side_effects=const_data.get("side_effects", ["none"]),
            data_retention=const_data.get("data_retention", "none")
        )
        
        # Parse connection
        conn_data = data.get("connection", {})
        modes = []
        for mode_data in conn_data.get("modes", []):
            modes.append(ConnectionMode(
                type=mode_data.get("type", ""),
                detail=mode_data.get("detail", "")
            ))
        connection = Connection(modes=modes)
        
        # Parse optional security profile
        security = None
        if "security" in data:
            sec_data = data["security"]
            security = SecurityProfile(
                fingerprint=sec_data.get("fingerprint"),
                publisher=sec_data.get("publisher"),
                signatures=sec_data.get("signatures", []),
                audit_url=sec_data.get("audit_url"),
                vulnerability_disclosure=sec_data.get("vulnerability_disclosure")
            )
        
        # Parse optional privacy profile
        privacy = None
        if "privacy" in data:
            priv_data = data["privacy"]
            privacy = PrivacyProfile(
                data_location=priv_data.get("data_location", []),
                encryption=priv_data.get("encryption", []),
                pii_handling=priv_data.get("pii_handling"),
                data_deletion=priv_data.get("data_deletion")
            )
        
        # Parse optional compliance
        compliance = None
        if "compliance" in data:
            comp_data = data["compliance"]
            compliance = ComplianceInfo(
                standards=comp_data.get("standards", []),
                certifications=comp_data.get("certifications", [])
            )
        
        # Parse optional cost profile
        cost = None
        if "cost" in data:
            cost_data = data["cost"]
            estimates = []
            for est in cost_data.get("estimates", []):
                estimates.append(CostEstimate(
                    input=est.get("input", ""),
                    cost=est.get("cost", ""),
                    latency_p50=est.get("latency_p50"),
                    latency_p99=est.get("latency_p99")
                ))
            cost = CostProfile(
                model=cost_data.get("model"),
                currency=cost_data.get("currency", "USD"),
                estimates=estimates,
                free_tier=cost_data.get("free_tier")
            )
        
        # Parse optional performance
        performance = None
        if "performance" in data:
            perf_data = data["performance"]
            performance = PerformanceInfo(
                availability=perf_data.get("availability"),
                rate_limit=perf_data.get("rate_limit"),
                max_payload=perf_data.get("max_payload")
            )
        
        return UTCDDescriptor(
            utcd_version=data.get("utcd_version", "1.0"),
            identity=identity,
            capability=capability,
            constraints=constraints,
            connection=connection,
            security=security,
            privacy=privacy,
            compliance=compliance,
            cost=cost,
            performance=performance,
            source_path=source_path
        )
    
    @staticmethod
    def load_directory(directory: str | Path) -> List[UTCDDescriptor]:
        """Load all UTCD descriptors from a directory."""
        directory = Path(directory)
        descriptors = []
        
        for path in directory.glob("*.utcd.yaml"):
            try:
                descriptors.append(UTCDLoader.load(path))
            except Exception as e:
                print(f"Warning: Failed to load {path}: {e}")
        
        return descriptors
