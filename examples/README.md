# RepoMesh AI - Examples

This directory contains example scripts demonstrating how to use RepoMesh AI.

## Prerequisites

Before running the examples, ensure you have:

1. Installed RepoMesh AI:
   ```bash
   pip install -r requirements.txt
   ```

2. Configured your environment:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

## Examples

### 1. Register Repositories (`register_repos.py`)

Demonstrates how to register repositories for analysis.

**Features**:
- Register local repositories
- Clone and register remote repositories
- List all registered repositories

**Usage**:
```bash
python examples/register_repos.py
```

**Interactive prompts**:
- Enter path to local repository (or skip)
- Enter Git repository URL (or skip)

**Example**:
```bash
$ python examples/register_repos.py
🚀 RepoMesh AI - Repository Registration Example
============================================================
✓ Repository manager initialized

📁 Example 1: Registering local repository...
Enter path to local repository (or press Enter to skip): /path/to/my-app
✓ Registered local repository: my-app
  - ID: 550e8400-e29b-41d4-a716-446655440000
  - Type: fullstack
  - Files: 150 (85 code files)
  - Lines: 12,500
  - Tech Stack: React, FastAPI, PostgreSQL
```

---

### 2. Run Orchestration (`run_orchestration.py`)

Demonstrates how to run multi-agent orchestration workflows.

**Features**:
- List registered repositories
- Select repositories to analyze
- Run orchestration workflow
- View agent results
- Display context updates

**Usage**:
```bash
python examples/run_orchestration.py
```

**Interactive prompts**:
- Select repositories by number or 'all'

**Example**:
```bash
$ python examples/run_orchestration.py
🚀 RepoMesh AI - Orchestration Example
============================================================
Initializing components...
✓ Components initialized

📋 Found 2 registered repositories:
1. frontend-app (frontend) - ID: 550e8400-e29b-41d4-a716-446655440000
2. backend-api (backend) - ID: 660e8400-e29b-41d4-a716-446655440001

🎯 Select repositories to analyze:
Enter repository numbers (comma-separated, or 'all'): all

🔄 Starting orchestration for 2 repositories...
------------------------------------------------------------

✓ Orchestration completed!
============================================================
Execution Time: 12.50s
Total Tasks: 4
Completed: 4
Failed: 0

📊 Agent Results:
------------------------------------------------------------
...
```

---

### 3. Inspect Context (`inspect_context.py`)

Demonstrates how to query and inspect shared context.

**Features**:
- List all context keys
- Search context by query
- View specific context entries
- Interactive exploration

**Usage**:
```bash
python examples/inspect_context.py
```

**Interactive menu**:
1. Search context
2. View specific context entry
3. List all keys
4. Exit

**Example**:
```bash
$ python examples/inspect_context.py
🚀 RepoMesh AI - Context Inspection Example
============================================================
✓ Context manager initialized

📋 Listing all context keys...
Found 5 context entries:
1. architecture:550e8400:frontend
2. api_contract:660e8400:backend_api
3. component:550e8400:UserProfile
4. ui_patterns:550e8400
5. dependency:660e8400:services

============================================================
Options:
1. Search context
2. View specific context entry
3. List all keys
4. Exit

Enter your choice (1-4): 1
Enter search query: API
...
```

---

## Running Examples in Order

For the best experience, run the examples in this order:

1. **First**: `register_repos.py` - Register some repositories
2. **Second**: `run_orchestration.py` - Analyze the repositories
3. **Third**: `inspect_context.py` - Explore the generated context

## Using with the API

You can also interact with RepoMesh AI through the REST API:

1. Start the API server:
   ```bash
   uvicorn repomesh.api.main:app --reload
   ```

2. Visit the interactive documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. Use curl or any HTTP client:
   ```bash
   # Register a repository
   curl -X POST http://localhost:8000/api/v1/repos/register \
     -H "Content-Type: application/json" \
     -d '{"path": "/path/to/repo"}'
   
   # Run orchestration
   curl -X POST http://localhost:8000/api/v1/orchestrate \
     -H "Content-Type: application/json" \
     -d '{"repo_ids": ["550e8400-e29b-41d4-a716-446655440000"]}'
   
   # Search context
   curl -X POST http://localhost:8000/api/v1/context/search \
     -H "Content-Type: application/json" \
     -d '{"query": "components", "top_k": 5}'
   ```

## Troubleshooting

### Import Errors

If you see import errors:
```bash
pip install -e .
```

### No Repositories Found

If `run_orchestration.py` shows no repositories:
```bash
python examples/register_repos.py
```

### No Context Found

If `inspect_context.py` shows no context:
```bash
python examples/run_orchestration.py
```

### OpenAI API Errors

Ensure your `.env` file has a valid `OPENAI_API_KEY`:
```bash
OPENAI_API_KEY=sk-...
```

## Advanced Usage

### Custom Configuration

You can modify the examples to use custom configuration:

```python
from repomesh.utils.config import Settings

settings = Settings(
    repos_base_path="./my-repos",
    max_concurrent_agents=10,
    log_level="DEBUG"
)
```

### Using ChromaDB

To use ChromaDB instead of in-memory storage:

```python
from repomesh.context.store import ChromaDBStore

context_store = ChromaDBStore(
    collection_name="my_context",
    persist_directory="./my-chroma-data"
)
```

### Event Monitoring

To monitor events during orchestration:

```python
from repomesh.core.events import EventBus, EventType

event_bus = EventBus()

async def on_task_completed(event):
    print(f"Task completed: {event.payload}")

event_bus.subscribe(EventType.TASK_COMPLETED, on_task_completed)
```

## Next Steps

- Read the [API Documentation](../docs/api.md)
- Explore the [Architecture](../ARCHITECTURE.md)
- Check the [Technical Specifications](../TECHNICAL_SPEC.md)
- Review the [Development Guide](../docs/development.md)

## Support

For issues or questions:
- GitHub Issues: https://github.com/repomesh/repomesh-ai/issues
- Documentation: https://docs.repomesh.ai