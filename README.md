# Production Health Guardian

A production health monitoring system designed to monitor and analyze hardware performance metrics.

## Features

- Real-time Hardware Metrics Collection
  - CPU metrics (usage, frequency, cores, context switches)
  - GPU metrics (temperature, utilization, memory usage, power)
  - Memory metrics (virtual and swap memory usage)
  - Extensible collector architecture for future metrics

- Monitoring Stack Integration
  - Prometheus metrics export with standard `/metrics` endpoint
  - Pre-configured Grafana dashboards
  - Real-time visualization of system performance
  - Historical data analysis and trending

- Modern API Design
  - RESTful API with OpenAPI/Swagger documentation
  - Prometheus and JSON output formats
  - Async operations for better performance
  - Comprehensive error handling

- Developer-Friendly
  - Type-safe Python codebase
  - Extensive test coverage
  - Docker and Docker Compose support
  - CI/CD with GitHub Actions

## Quick Start (Production)

1. Make sure you have Docker and Docker Compose installed.

2. Clone the repository and start all services:
```bash
docker-compose up -d
```

3. Access the services:
- Production Health Guardian API:
  - Root URL (redirects to docs): http://localhost:8000
  - Metrics (Prometheus format): http://localhost:8000/metrics
  - Metrics (JSON format): http://localhost:8000/metrics/json
  - API Documentation: http://localhost:8000/api/docs
- Prometheus: http://localhost:9090
- Grafana: http://localhost:3000 (login with admin/admin)

### Monitoring Dashboard

The system comes with a pre-configured Grafana dashboard that provides:
- CPU metrics (usage per core, frequency)
- GPU metrics (temperature, utilization, memory)
- Memory metrics (virtual and swap usage)
- System events (context switches, interrupts)

To access the dashboard:
1. Open Grafana at http://localhost:3000
2. Log in with default credentials (admin/admin)
3. Navigate to Dashboards > Browse
4. Select "Production Health Guardian Dashboard"

If you need to reimport the dashboard manually:
1. Go to Dashboards > Import
2. Upload `config/grafana/grafana-dashboard.json`

## Development Setup

1. Install Poetry (if not already installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Install dependencies:
```bash
# Install all dependencies (including dev)
poetry install
```

3. Run tests:
```bash
poetry run pytest
```

4. Start the local development server:
```bash
# Starts the FastAPI server with hot-reload enabled
poetry run uvicorn prod_health_guardian.api.main:app --reload
```

The server will be available at http://localhost:8000 with hot-reload enabled for development.

### Development Tools

- Add a new dependency: `poetry add package-name`
- Add a dev dependency: `poetry add --group dev package-name`
- Update dependencies: `poetry update`
- Show dependency tree: `poetry show --tree`
- Run a command in the virtual environment: `poetry run command`
- Activate the virtual environment: `poetry shell`

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

## Troubleshooting

1. Check service status:
```bash
docker-compose ps
```

2. View service logs:
```bash
# All services
docker-compose logs

# Specific service
docker-compose logs [service_name]  # app, prometheus, or grafana
```

3. Common issues:
- If Grafana can't connect to Prometheus, ensure both services are on the same Docker network
- If metrics aren't showing, check Prometheus targets at http://localhost:9090/targets
- For application issues, check the logs with `docker-compose logs app`

## Project Structure

```
prod-health-guardian/
├── config/                # Configuration files
│   ├── prometheus/       # Prometheus configurations
│   │   └── prometheus.yml
│   └── grafana/         # Grafana configurations
│       ├── datasources.yml
│       └── dashboard.json
├── src/
│   └── prod_health_guardian/
│       ├── api/         # FastAPI application
│       ├── collectors/  # Hardware metric collectors
│       ├── metrics/     # Metrics formatters (Prometheus)
│       ├── models/      # Data models
│       └── utils/       # Utility functions
├── tests/               # Test suite
├── scripts/            # Development scripts
├── .github/            # GitHub Actions workflows
└── pyproject.toml      # Project and dependency configuration
```

## API Documentation

The API documentation is available in two different UI formats:
- OpenAPI UI (Swagger): http://localhost:8000/api/docs
- ReDoc UI: http://localhost:8000/api/redoc

Choose the UI that best suits your needs - OpenAPI UI for testing and interaction, ReDoc for reading and reference.

### API Endpoints

The API provides the following main endpoints:

#### System Endpoints
- Health check and system information
- API documentation (OpenAPI and ReDoc)

#### Metrics Endpoints
- Prometheus format: `/metrics`
- JSON format: `/metrics/json` and specific collector endpoints

For detailed API documentation, parameter descriptions, and response formats, please refer to the OpenAPI documentation at http://localhost:8000/api/docs

## Monitoring Stack

### Configuration Files

The monitoring stack configuration is stored in:

- `docker-compose.yml`: Main configuration for all services
- `config/prometheus/prometheus.yml`: Prometheus scraping configuration
- `config/grafana/datasources.yml`: Grafana datasource configuration
- `config/grafana/grafana-dashboard.json`: Pre-configured Grafana dashboard

## Continuous Integration

This project uses GitHub Actions for continuous integration:

- **Python Tests**: Runs on every push and pull request
  - Runs tests on Python 3.9 and 3.10
  - Uploads test coverage to Codecov

- **Python Lint**: Runs on every push and pull request
  - Performs code linting with Ruff
  - Uses Python 3.10

## Development Guidelines

- Code style is enforced using `ruff`
- Tests are written using `pytest`
- Type hints are required for all functions
- Documentation follows PEP 257

## Security

### Best Practices

- All API endpoints use HTTPS in production
- Grafana access is protected by authentication
- Environment variables are used for sensitive configuration
- Docker containers run with non-root users
- Regular dependency updates via Poetry

### Environment Variables

Required environment variables:
- `GRAFANA_ADMIN_PASSWORD`: Grafana admin password (default: admin)
- `PROMETHEUS_RETENTION_DAYS`: Data retention period (default: 15)

Optional environment variables:
- `DEBUG`: Enable debug mode (default: False)
- `LOG_LEVEL`: Logging level (default: INFO)
- `API_KEY`: Optional API key for secured endpoints

## Architecture

### Metrics Collection

The application uses a modular metrics collection system:

1. **Collectors**: Individual collectors (`CPUCollector`, `MemoryCollector`) gather raw metrics from the system.
2. **Models**: Pydantic models validate and structure the collected data.
3. **MetricsCollector**: A central coordinator that:
   - Manages individual collectors
   - Validates metrics through models
   - Converts metrics to various formats (Prometheus, JSON)

The metrics flow is:
```
Hardware Collectors -> Pydantic Models -> MetricsCollector -> Prometheus/JSON Export
```
