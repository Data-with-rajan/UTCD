"""
UTCD Signer - Utility for generating cryptographic signatures for UTCD descriptors.
"""

import json
import yaml
import copy
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, Union

try:
    from cryptography.hazmat.primitives.asymmetric import ed25519
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

class UTCDSigner:
    """Utility for signing UTCD descriptors using canonical hashing."""
    
    def __init__(self, private_key_path: Optional[Union[str, Path]] = None):
        if not HAS_CRYPTOGRAPHY:
            raise ImportError("The 'cryptography' library is required for signing. Install it with 'pip install cryptography'.")
        
        self.private_key_path = Path(private_key_path) if private_key_path else None
        self.private_key = None
        self.public_key = None
        
        if self.private_key_path and self.private_key_path.exists():
            self.load_keys(self.private_key_path)

    @staticmethod
    def generate_keys(path_prefix: Union[str, Path]) -> Tuple[Path, Path]:
        """Generate a new Ed25519 key pair."""
        prefix = Path(path_prefix)
        priv_path = prefix.with_suffix(".key")
        pub_path = prefix.with_suffix(".pub")
        
        private_key = ed25519.Ed25519PrivateKey.generate()
        public_key = private_key.public_key()
        
        # Save private key (hex format for simplicity in v1)
        priv_bytes = private_key.private_bytes_raw()
        with open(priv_path, "w") as f:
            f.write(priv_bytes.hex())
            
        # Save public key
        pub_bytes = public_key.public_bytes_raw()
        with open(pub_path, "w") as f:
            f.write(pub_bytes.hex())
            
        return priv_path, pub_path

    def load_keys(self, private_key_path: Union[str, Path]):
        """Load keys from a private key file."""
        priv_path = Path(private_key_path)
        with open(priv_path, "r") as f:
            priv_hex = f.read().strip()
            
        self.private_key = ed25519.Ed25519PrivateKey.from_private_bytes(bytes.fromhex(priv_hex))
        self.public_key = self.private_key.public_key()

    def get_public_key_hex(self) -> str:
        """Get the public key in hex format."""
        if not self.public_key:
            raise ValueError("No keys loaded.")
        return self.public_key.public_bytes_raw().hex()

    def canonicalize(self, data: Dict[str, Any]) -> bytes:
        """Generate a canonical JSON representation of the descriptor."""
        clean_data = copy.deepcopy(data)
        
        # Remove security block (Fix #3: Shadow Capability Protection)
        if "security" in clean_data:
            del clean_data["security"]
            
        # Create canonical JSON string (sorted keys, no whitespace)
        canonical_json = json.dumps(clean_data, sort_keys=True, separators=(',', ':'))
        return canonical_json.encode('utf-8')

    def sign(self, descriptor_data: Dict[str, Any]) -> str:
        """Sign a descriptor and return the signature hex."""
        if not self.private_key:
            raise ValueError("Private key not loaded. Call load_keys or initialize with a key path.")
            
        message = self.canonicalize(descriptor_data)
        signature_bytes = self.private_key.sign(message)
        return signature_bytes.hex()

    def sign_file(self, file_path: Union[str, Path], publisher_did: Optional[str] = None):
        """Sign a UTCD YAML file and update it with a security profile."""
        path = Path(file_path)
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            
        signature_hex = self.sign(data)
        public_key_hex = self.get_public_key_hex()
        
        # Initialize security profile if missing
        if "security" not in data:
            data["security"] = {}
            
        if publisher_did:
            data["security"]["publisher"] = publisher_did
            
        if "signatures" not in data["security"]:
            data["security"]["signatures"] = []
            
        # Add signature (alg: ed25519)
        data["security"]["signatures"].append({
            "alg": "ed25519",
            "public_key": public_key_hex,
            "signature": signature_hex
        })
        
        # Save updated YAML
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, sort_keys=False, indent=2)
        
        return signature_hex
