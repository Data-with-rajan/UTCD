import json
import yaml
from pathlib import Path

try:
    from jsonschema import validate, ValidationError
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False

def test_abc_validation():
    base_dir = Path(__file__).parent.parent
    schema_path = base_dir / "abc" / "abc-schema.json"
    examples_dir = base_dir / "abc" / "examples"
    
    with open(schema_path, "r") as f:
        schema = json.load(f)
    
    examples = list(examples_dir.glob("*.abc.yaml"))
    
    if not examples:
        print("No examples found!")
        return
    
    all_passed = True
    for example_path in examples:
        with open(example_path, "r") as f:
            data = yaml.safe_load(f)
        
        if HAS_JSONSCHEMA:
            try:
                validate(instance=data, schema=schema)
                print(f"✓ {example_path.name} is valid (jsonschema).")
            except ValidationError as e:
                print(f"✗ {example_path.name} failed jsonschema validation:")
                print(f"  Path: {list(e.path)}")
                print(f"  Message: {e.message}")
                all_passed = False
        else:
            # Basic fallback validation
            required_top = schema.get("required", [])
            missing = [k for k in required_top if k not in data]
            if not missing:
                print(f"✓ {example_path.name} has all required top-level keys.")
            else:
                print(f"✗ {example_path.name} is missing required keys: {missing}")
                all_passed = False
    
    if all_passed:
        if not HAS_JSONSCHEMA:
            print("\nNote: jsonschema not found. Performed basic key presence check.")
        print("ABC examples passed validation.")
    else:
        exit(1)

if __name__ == "__main__":
    test_abc_validation()

if __name__ == "__main__":
    test_abc_validation()
