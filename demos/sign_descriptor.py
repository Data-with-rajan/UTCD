"""
Demo script for signing a UTCD descriptor.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path.cwd()))

from utcd.signer import UTCDSigner

def main():
    if len(sys.argv) < 2:
        print("Usage: python demos/sign_descriptor.py <file.utcd.yaml> [publisher_did]")
        sys.exit(1)
        
    file_path = Path(sys.argv[1])
    publisher_did = sys.argv[2] if len(sys.argv) > 2 else "did:utcd:test-publisher"
    
    key_path = Path(".utcd_key.key")
    
    if not key_path.exists():
        print(f"Keys not found. Generating new keys at {key_path}...")
        UTCDSigner.generate_keys(".utcd_key")
        
    signer = UTCDSigner(".utcd_key.key")
    print(f"Signing {file_path}...")
    
    try:
        sig = signer.sign_file(file_path, publisher_did=publisher_did)
        print(f"✓ Successfully signed!")
        print(f"  Public Key: {signer.get_public_key_hex()}")
        print(f"  Signature:  {sig[:16]}...")
        print(f"  Updated: {file_path}")
    except Exception as e:
        print(f"✗ Signing failed: {e}")

if __name__ == "__main__":
    main()
