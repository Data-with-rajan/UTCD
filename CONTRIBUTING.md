# Contributing to UTCD

Thank you for your interest in contributing to UTCD!

## Ways to Contribute

### 1. Report Issues
- Found a bug in the validator? Open an issue.
- Unclear documentation? Let us know.
- Have a question? Start a discussion.

### 2. Improve Documentation
- Fix typos and clarify wording
- Add examples
- Translate to other languages

### 3. Add Examples
- Create UTCD files for real tools
- Share interesting use cases
- Document integration patterns

### 4. Contribute Code
- Fix bugs in validator/agent
- Add new policy types
- Improve error messages

### 5. Propose Profiles
- Identify a missing use case
- Draft a profile schema
- Provide a reference implementation

## Development Setup

```bash
# Clone the repo
git clone https://github.com/your-org/utcd.git
cd utcd

# Install dependencies
pip install pyyaml pytest

# Run tests
python -m pytest tests/ -v
```

## Pull Request Guidelines

1. **One change per PR** — Keep PRs focused
2. **Add tests** — New features need tests
3. **Update docs** — If behavior changes, update docs
4. **Follow style** — Match existing code style

## Core vs Profiles

| Type | Can be changed? |
|------|-----------------|
| Core schema | ❌ Frozen after v1 |
| Profiles | ✅ Evolve via community |
| Reference implementation | ✅ Improvements welcome |

## Code of Conduct

Be respectful. Be constructive. Focus on the work.

## Questions?

Open an issue or start a discussion. We're happy to help!
