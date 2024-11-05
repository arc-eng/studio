# Use the official Python image from the Docker Hub
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


# Install system dependencies required for uWSGI compilation
RUN apt-get update && apt-get install -y \
    gcc \
    libc6-dev \
    libpcre3-dev \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -y --only-upgrade openssl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /code

# Install dependencies
COPY pyproject.toml poetry.lock /code/
RUN pip install --no-cache-dir poetry uvicorn \
    && poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy project
COPY . /code/

# Expose port 8000 for uwsgi
EXPOSE 8000

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl --fail http://localhost:8000/ || exit 1

CMD ["sh", "-c", "uvicorn --host 0.0.0.0 --port 8000 studio.asgi:application"]
