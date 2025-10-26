# Use Python 3.13 slim image
FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml ./ uv.lock* ./

# Install uv (Python package manager)
RUN pip install uv

# Install dependencies using uv sync
RUN uv sync

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Set Python path
ENV PYTHONPATH=/app

# Default command (will be overridden in docker-compose)
CMD ["python", "app/redis_reciever.py"]
