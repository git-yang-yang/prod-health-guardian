# Production Health Guardian

A production health monitoring system designed to monitor and analyze hardware performance metrics.

## Features

- Hardware telemetry collection (CPU, Memory, Disk, Network)
- Performance metrics monitoring and analysis
- RESTful API for metrics access
- Prometheus metrics export
- Alerting system for threshold violations

## Setup

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
# Install all dependencies (including dev)
poetry install

# Install only production dependencies
poetry install --without dev
```

3. Run tests:
```bash
poetry run pytest
```

4. Start the service:
```bash
poetry run uvicorn prod_health_guardian.api.main:app --reload
```

## Project Structure

```
prod-health-guardian/
├── src/
│   └── prod_health_guardian/
│       ├── api/            # FastAPI application
│       ├── collectors/     # Hardware metric collectors
│       ├── models/         # Data models
│       └── utils/          # Utility functions
├── tests/                  # Test suite
├── scripts/               # Development scripts
├── .github/               # GitHub Actions workflows
└── pyproject.toml         # Project and dependency configuration
```

## Development

- Code style is enforced using `ruff`
- Tests are written using `pytest`
- Type hints are required for all functions
- Documentation follows PEP 257

### Local Development Checks

Before pushing your changes, run the local checks script:
```bash
./scripts/check.sh
```

This script will:
1. Verify Poetry is installed
2. Install/update dependencies
3. Run linting with Ruff
4. Run tests with coverage report

The script mimics the CI pipeline checks, helping catch issues before pushing to GitHub.

## Using Poetry

- Add a new dependency: `poetry add package-name`
- Add a dev dependency: `poetry add --group dev package-name`
- Update dependencies: `poetry update`
- Show dependency tree: `poetry show --tree`
- Run a command in the virtual environment: `poetry run command`
- Activate the virtual environment: `poetry shell`

## Continuous Integration

This project uses GitHub Actions for continuous integration:

- **Python Tests**: Runs on every push and pull request
  - Runs tests on Python 3.9 and 3.10
  - Uploads test coverage to Codecov

- **Python Lint**: Runs on every push and pull request
  - Performs code linting with Ruff
  - Uses Python 3.10
