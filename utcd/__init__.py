"""
UTCD - Universal Tool Capability Descriptor

A minimal, execution-agnostic descriptor system for AI tool capabilities.
"""

__version__ = "1.0.0"

from .loader import UTCDLoader, UTCDDescriptor
from .signer import UTCDSigner
from .validator import UTCDValidator, ValidationResult
from .agent import UTCDAgent, Policy, Decision, RiskLevel, RiskEngine

__all__ = [
    "UTCDLoader",
    "UTCDDescriptor", 
    "UTCDSigner",
    "UTCDValidator",
    "ValidationResult",
    "UTCDAgent",
    "Policy",
    "Decision",
    "RiskLevel",
    "RiskEngine",
]
