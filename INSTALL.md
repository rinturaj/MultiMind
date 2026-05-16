# RepoMesh AI - Installation Guide

## Prerequisites

- Python 3.11 or higher
- Git
- OpenAI API key (for LLM features)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/repomesh/repomesh-ai.git
cd repomesh-ai
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

#### Option A: Using pip
```bash
pip install -r requirements.txt
```

#### Option B: Using pip with development dependencies
```bash
pip install -r requirements-dev.txt
```

#### Option C: Using setup.py
```bash
pip install -e .
```

#### Option D: Using setup.py with development dependencies
```bash
pip install -e ".[dev]"
```

### 4. Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and set your configuration:

```env
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional (defaults provided)
OPENAI_MODEL=gpt-4-turbo-preview
API_HOST=0.0.0.0
API_PORT=8000
REPOS_BASE_PATH=./repos
CHROMA_PERSIST_DIRECTORY=./data/chroma
```

### 5. Verify Installation

```bash
python -c "import repomesh; print('RepoMesh AI installed successfully!')"
```

## Quick Start

### Start the API Server

```bash
# Development mode with auto-reload
uvicorn repomesh.api.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn repomesh.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Documentation**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## Testing the Installation

### 1. Check Health Endpoint

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "RepoMesh AI"
}
```

### 2. Register a Repository

```bash
curl -X POST http://localhost:8000/api/v1/repos/register \
  -H "Content-Type: application/json" \
  -d '{
    "path": "/path/to/your/repository"
  }'
```

### 3. Run Orchestration

```bash
curl -X POST http://localhost:8000/api/v1/orchestrate \
  -H "Content-Type: application/json" \
  -d '{
    "repo_ids": ["<repo-id-from-previous-step>"]
  }'
```

## Troubleshooting

### Import Errors

If you see import errors, ensure:
1. Virtual environment is activated
2. All dependencies are installed: `pip install -r requirements.txt`
3. Package is installed in development mode: `pip install -e .`

### ChromaDB Issues

If ChromaDB fails to initialize:
```bash
pip install --upgrade chromadb
```

### LangGraph Issues

If LangGraph fails:
```bash
pip install --upgrade langgraph langchain langchain-openai
```

### Port Already in Use

If port 8000 is already in use:
```bash
uvicorn repomesh.api.main:app --port 8001
```

## Development Setup

### Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest
```

### Run Linting

```bash
# Format code
black src/

# Lint code
ruff check src/

# Type checking
mypy src/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Docker Installation (Optional)

### Build Docker Image

```bash
docker build -t repomesh-ai .
```

### Run Docker Container

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key_here \
  -v $(pwd)/repos:/app/repos \
  -v $(pwd)/data:/app/data \
  repomesh-ai
```

## Next Steps

- Read the [Architecture Documentation](ARCHITECTURE.md)
- Check the [API Documentation](docs/api.md)
- Explore [Example Scripts](examples/)
- Review [Development Guide](docs/development.md)

## Support

For issues and questions:
- GitHub Issues: https://github.com/repomesh/repomesh-ai/issues
- Documentation: https://docs.repomesh.ai
- Email: support@repomesh.ai