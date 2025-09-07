# syntax=docker/dockerfile:1
FROM python:3.11-slim as base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl && \
    rm -rf /var/lib/apt/lists/*

# Copy only dependency files first for layer caching
COPY pyproject.toml requirements.txt ./

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy source
COPY . .

# Default command shows CLI help; override in compose or kubernetes
CMD ["python", "-m", "src.cli", "--help"]
