# Production Health Guardian

A production health monitoring system designed to monitor and analyze hardware performance metrics.

## Features

- Real-time Hardware Metrics Collection
  - CPU metrics (usage, frequency, cores, context switches)
  - Memory metrics (virtual and swap memory usage)
  - Extensible collector architecture for future metrics

- Monitoring Stack Integration
  - Prometheus metrics export with standard `/metrics` endpoint
  - Pre-configured Grafana dashboards
  - Real-time visualization of system performance
  - Historical data analysis and trending

- Modern API Design
  - RESTful API with OpenAPI/Swagger documentation
  - JSON and Prometheus output formats
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

### Monitoring Dashboard Setup

The monitoring stack comes with pre-configured dashboards for immediate insights:

#### Grafana Dashboards
The included Grafana dashboard provides:
- CPU Usage (total and per core)
- Memory Usage (virtual and swap)
- System Events (context switches, interrupts)
- Hardware Information (CPU cores, frequencies)

To access the dashboards:
1. Open Grafana at http://localhost:3000
2. Log in with default credentials (admin/admin)
3. Navigate to Dashboards > Browse
4. Select "Production Health Guardian Dashboard"

#### Custom Dashboard Import
If you need to reimport the dashboard:
1. Go to Dashboards > Import
2. Upload the JSON file from `config/grafana/grafana-dashboard.json`

#### Prometheus Data Source
Prometheus is automatically configured as a data source in Grafana. To verify:
1. Go to Configuration > Data Sources
2. Check that Prometheus is listed and healthy
3. Default URL should be `http://prometheus:9090`

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

4. Start the development server:
```bash
poetry run uvicorn prod_health_guardian.api.main:app --reload
```

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

## Manual Service Setup

If you prefer to run services individually without Docker Compose:

### Prometheus Setup

Using Docker:
```bash
docker run -d \
    --name prometheus \
    -p 9090:9090 \
    -v $(pwd)/config/prometheus:/etc/prometheus \
    prom/prometheus
```

Or locally with Homebrew:
```bash
brew install prometheus
# Copy config
cp config/prometheus/prometheus.yml /usr/local/etc/prometheus/prometheus.yml
# Start service
brew services start prometheus
```

### Grafana Setup

Using Docker:
```bash
docker run -d \
    --name grafana \
    -p 3000:3000 \
    -v $(pwd)/config/grafana:/etc/grafana/provisioning \
    grafana/grafana
```

Or locally with Homebrew:
```bash
brew install grafana
# Start service
brew services start grafana
```

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

The API documentation is available at:
- OpenAPI UI: `/api/docs`
- ReDoc UI: `/api/redoc`

### API Endpoints

#### System Endpoints
- `GET /`: Redirects to API documentation
- `GET /health`: Health check endpoint
- `GET /api/docs`: OpenAPI documentation (Swagger UI)
- `GET /api/redoc`: ReDoc documentation

#### Metrics Endpoints

##### Prometheus Format

```
GET /metrics
```

This endpoint returns metrics in the Prometheus text format. Available metrics:

###### CPU Metrics
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

###### Memory Metrics
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

###### GPU Metrics
- `gpu_device_count`: Number of NVIDIA GPUs available
- `gpu_temperature_celsius{gpu_id="N",name="GPU_NAME"}`: GPU temperature in Celsius
- `gpu_power_watts{gpu_id="N",name="GPU_NAME"}`: GPU power usage in Watts
- `gpu_memory_total_bytes{gpu_id="N",name="GPU_NAME"}`: Total GPU memory in bytes
- `gpu_memory_used_bytes{gpu_id="N",name="GPU_NAME"}`: Used GPU memory in bytes
- `gpu_memory_free_bytes{gpu_id="N",name="GPU_NAME"}`: Free GPU memory in bytes
- `gpu_utilization_percent{gpu_id="N",name="GPU_NAME"}`: GPU utilization percentage
- `gpu_memory_utilization_percent{gpu_id="N",name="GPU_NAME"}`: GPU memory utilization percentage
- `gpu_fan_speed_percent{gpu_id="N",name="GPU_NAME"}`: GPU fan speed percentage

##### JSON Format

For custom integrations and detailed metrics:

- `GET /metrics/json`: Get all system metrics in JSON format
- `GET /metrics/json/cpu`: Get CPU-specific metrics
- `GET /metrics/json/memory`: Get memory-specific metrics
- `GET /metrics/json/gpu`: Get GPU-specific metrics

Example JSON response for `/metrics/json/cpu`:
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
  }
}
```

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
