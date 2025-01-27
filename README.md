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

## API Endpoints

The service provides both Prometheus and JSON format metrics:

### Prometheus Metrics (Standard)

The standard Prometheus metrics endpoint:
```
GET /metrics
```

This endpoint returns metrics in the Prometheus text format, following standard conventions for metric exposition.

Available metrics:

#### CPU Metrics
- `cpu_physical_count`: Number of physical CPU cores
- `cpu_logical_count`: Number of logical CPU cores
- `cpu_frequency_current_mhz`: Current CPU frequency in MHz
- `cpu_frequency_min_mhz`: Minimum CPU frequency in MHz
- `cpu_frequency_max_mhz`: Maximum CPU frequency in MHz
- `cpu_percent_total`: Total CPU usage percentage
- `cpu_percent_per_cpu{core="N"}`: CPU usage percentage per core
- `cpu_ctx_switches_total`: Total context switches
- `cpu_interrupts_total`: Total hardware interrupts
- `cpu_soft_interrupts_total`: Total software interrupts
- `cpu_syscalls_total`: Total system calls

#### Memory Metrics
- `memory_virtual_total_bytes`: Total virtual memory in bytes
- `memory_virtual_available_bytes`: Available virtual memory in bytes
- `memory_virtual_used_bytes`: Used virtual memory in bytes
- `memory_virtual_free_bytes`: Free virtual memory in bytes
- `memory_virtual_percent`: Virtual memory usage percentage
- `memory_swap_total_bytes`: Total swap memory in bytes
- `memory_swap_used_bytes`: Used swap memory in bytes
- `memory_swap_free_bytes`: Free swap memory in bytes
- `memory_swap_percent`: Swap memory usage percentage
- `memory_swap_sin_total`: Total memory pages swapped in
- `memory_swap_sout_total`: Total memory pages swapped out

### JSON Endpoints

For custom integrations and detailed metrics:

- `GET /metrics/json`: Get all system metrics in JSON format
- `GET /metrics/json/cpu`: Get CPU-specific metrics
- `GET /metrics/json/memory`: Get memory-specific metrics
- `GET /health`: Health check endpoint

Example JSON response for `/metrics/json`:
```json
{
  "cpu": {
    "count": {
      "physical": 4,
      "logical": 8
    },
    "frequency": {
      "current": 2400.0,
      "min": 2200.0,
      "max": 3200.0
    },
    "percent": {
      "total": 25.5,
      "per_cpu": [20.0, 30.0, 25.0, 27.0]
    },
    "stats": {
      "ctx_switches": 1000,
      "interrupts": 500,
      "soft_interrupts": 200,
      "syscalls": 5000
    }
  },
  "memory": {
    "virtual": {
      "total": 16000000000,
      "available": 8000000000,
      "used": 7000000000,
      "free": 1000000000,
      "percent": 43.75
    },
    "swap": {
      "total": 8000000000,
      "used": 1000000000,
      "free": 7000000000,
      "percent": 12.5,
      "sin": 100,
      "sout": 50
    }
  }
}
```

## Prometheus Integration

Add the following to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'prod_health_guardian'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
```

## Project Structure

```
prod-health-guardian/
├── src/
│   └── prod_health_guardian/
│       ├── api/            # FastAPI application
│       ├── collectors/     # Hardware metric collectors
│       ├── metrics/        # Metrics formatters (Prometheus)
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

## API Documentation

The API documentation is available at:
- OpenAPI UI: `/api/docs`
- ReDoc UI: `/api/redoc`

## Continuous Integration

This project uses GitHub Actions for continuous integration:

- **Python Tests**: Runs on every push and pull request
  - Runs tests on Python 3.9 and 3.10
  - Uploads test coverage to Codecov

- **Python Lint**: Runs on every push and pull request
  - Performs code linting with Ruff
  - Uses Python 3.10
