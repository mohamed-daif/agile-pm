# Contributing to Agile-PM

Thank you for your interest in contributing to Agile-PM! This document provides guidelines for contributing.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### Reporting Bugs

1. Check existing issues to avoid duplicates
2. Use the bug report template
3. Include reproduction steps
4. Include version and environment info

### Suggesting Features

1. Check existing feature requests
2. Use the feature request template
3. Explain the use case and benefits

### Code Contributions

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Update documentation
6. Submit a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/agile-pm.git
cd agile-pm

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -e ".[dev,test]"

# Install pre-commit hooks
pre-commit install
```

## Code Style

- Python: Follow PEP 8, enforced by ruff
- TypeScript: Follow ESLint configuration
- Commits: Use [Conventional Commits](https://conventionalcommits.org)

### Running Checks

```bash
# Lint
ruff check src/ tests/

# Format
ruff format src/ tests/

# Type check
mypy src/

# Tests
pytest tests/
```

## Pull Request Process

1. Update the README.md if needed
2. Update the CHANGELOG.md
3. Ensure all checks pass
4. Request review from maintainers
5. Address review feedback

## Release Process

Releases are automated via GitHub Actions when a tag is pushed.

```bash
# Create release tag
git tag v0.2.0
git push origin v0.2.0
```

## Questions?

- Open a [Discussion](https://github.com/mohamed-daif/agile-pm/discussions)
- Join our community chat

Thank you for contributing! 🙏
