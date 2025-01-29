FROM python:3.10-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy project files
COPY pyproject.toml poetry.lock README.md ./

# Configure poetry to not create a virtual environment since we're in a container
RUN poetry config virtualenvs.create false \
    && poetry config installer.max-workers 4

# Copy application code
COPY src ./src

# Install dependencies and the package itself
RUN poetry install --only main --no-interaction --no-ansi \
    && pip install -e .

# Expose port
EXPOSE 8000

# Run the application
CMD ["poetry", "run", "uvicorn", "prod_health_guardian.api.main:app", "--host", "0.0.0.0", "--port", "8000"] 