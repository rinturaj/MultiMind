FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY pyproject.toml setup.py ./

# Install the package
RUN pip install -e .

# Create directories for data
RUN mkdir -p /app/repos /app/data/chroma /app/traces

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV REPOS_BASE_PATH=/app/repos
ENV CHROMA_PERSIST_DIRECTORY=/app/data/chroma
ENV TRACE_OUTPUT_DIR=/app/traces

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import httpx; httpx.get('http://localhost:8000/health')"

# Run the application
CMD ["uvicorn", "repomesh.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Made with Bob
