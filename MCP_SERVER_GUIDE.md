# RepoMesh MCP Server Guide

## Overview

The RepoMesh MCP Server exposes a multi-agent repository analysis system as Model Context Protocol (MCP) tools. This allows AI assistants to analyze codebases using specialized agents for frontend, backend, and other aspects of software development.

## Architecture

The system has been restructured to work as an MCP server with the following components:

### Core Components

1. **MCP Server** (`src/repomesh/mcp_server.py`)
   - Exposes all agent capabilities as MCP tools
   - Handles repository management
   - Coordinates multi-agent orchestration
   - Manages shared context between agents

2. **Specialized Agents**
   - **Frontend Agent**: Analyzes UI components, patterns, and API integrations
   - **Backend Agent**: Analyzes API endpoints, schemas, and service dependencies
   - Additional agents can be added for DevOps, Testing, Documentation, etc.

3. **Orchestration Workflow**
   - LangGraph-based workflow for coordinating multiple agents
   - Stateful execution with context sharing
   - Parallel agent execution where possible

4. **Shared Context Manager**
   - ChromaDB-backed vector store for semantic search
   - Stores API contracts, schemas, and architectural decisions
   - Enables cross-repository insights

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Edit the `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=your-actual-api-key-here
```

### 3. Start the MCP Server

```bash
python start_mcp_server.py
```

Or directly:

```bash
python -m repomesh.mcp_server
```

## Available MCP Tools

### Repository Management

#### `register_repository`
Clone and register a Git repository for analysis.

**Parameters:**
- `url` (string, required): Git repository URL
- `name` (string, optional): Custom repository name

**Example:**
```json
{
  "url": "https://github.com/user/repo.git",
  "name": "my-project"
}
```

#### `load_local_repository`
Load an existing local repository.

**Parameters:**
- `path` (string, required): Local path to repository
- `url` (string, optional): Remote URL for reference

#### `list_repositories`
List all registered repositories.

**Returns:** JSON array of repositories with metadata

#### `get_repository_details`
Get detailed information about a specific repository.

**Parameters:**
- `repo_id` (string, required): Repository UUID

### Agent Analysis

#### `analyze_frontend`
Run frontend-specific analysis on a repository.

**Parameters:**
- `repo_id` (string, required): Repository UUID

**Analyzes:**
- UI components (React, Vue, Svelte, etc.)
- UI patterns and libraries (Material-UI, Tailwind, etc.)
- API integrations and data fetching

**Returns:**
```json
{
  "success": true,
  "repo_name": "my-frontend",
  "agent": "frontend",
  "analysis": {
    "components": [...],
    "ui_patterns": [...],
    "api_integrations": [...],
    "summary": "..."
  }
}
```

#### `analyze_backend`
Run backend-specific analysis on a repository.

**Parameters:**
- `repo_id` (string, required): Repository UUID

**Analyzes:**
- API endpoints and routes
- Database schemas and migrations
- Service dependencies (databases, message queues, etc.)

**Returns:**
```json
{
  "success": true,
  "repo_name": "my-backend",
  "agent": "backend",
  "analysis": {
    "endpoints": [...],
    "schemas": [...],
    "dependencies": [...],
    "summary": "..."
  }
}
```

#### `run_full_analysis`
Run complete multi-agent orchestration workflow.

**Parameters:**
- `repo_ids` (string, required): Comma-separated list of repository UUIDs

**Returns:**
```json
{
  "success": true,
  "orchestration": {
    "total_steps": 5,
    "execution_time_seconds": 12.5,
    "completed_tasks": 4,
    "failed_tasks": 0,
    "task_results": [...],
    "shared_context_updates": 8
  }
}
```

### Context Management

#### `search_shared_context`
Search for API contracts, schemas, or architectural notes.

**Parameters:**
- `query` (string, required): Search query
- `repo_id` (string, optional): Filter to specific repository
- `top_k` (integer, optional): Number of results (default: 10)

#### `store_architecture_note`
Store an architectural decision or note.

**Parameters:**
- `content` (string, required): Note content
- `repo_id` (string, required): Repository UUID
- `agent_type` (string, optional): Agent type (default: "backend")

### Agent Information

#### `list_available_agents`
List all available agents and their capabilities.

#### `get_agent_capabilities`
Get capabilities of a specific agent.

**Parameters:**
- `agent_type` (string, required): Agent type (frontend, backend, etc.)

## Usage Examples

### Example 1: Analyze a Single Repository

```python
# 1. Register a repository
result = await register_repository(
    url="https://github.com/facebook/react.git"
)
repo_id = json.loads(result)["repo_id"]

# 2. Run frontend analysis
analysis = await analyze_frontend(repo_id=repo_id)
print(json.loads(analysis))
```

### Example 2: Multi-Repository Analysis

```python
# 1. Register multiple repositories
frontend_result = await register_repository(
    url="https://github.com/user/frontend.git"
)
backend_result = await register_repository(
    url="https://github.com/user/backend.git"
)

frontend_id = json.loads(frontend_result)["repo_id"]
backend_id = json.loads(backend_result)["repo_id"]

# 2. Run full orchestration
orchestration = await run_full_analysis(
    repo_ids=f"{frontend_id},{backend_id}"
)
print(json.loads(orchestration))

# 3. Search shared context
context = await search_shared_context(
    query="API endpoints",
    top_k=5
)
print(json.loads(context))
```

### Example 3: Store and Retrieve Architecture Notes

```python
# Store a note
await store_architecture_note(
    content="Using REST API with JWT authentication",
    repo_id=backend_id,
    agent_type="backend"
)

# Search for it later
results = await search_shared_context(
    query="authentication",
    repo_id=backend_id
)
```

## Integration with AI Assistants

The MCP server can be integrated with AI assistants like Claude, GPT-4, or other LLM-based tools that support the Model Context Protocol.

### Configuration Example (for Claude Desktop)

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "repomesh": {
      "command": "python",
      "args": ["C:/path/to/MultiMind/start_mcp_server.py"],
      "env": {
        "OPENAI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

## Advanced Features

### Custom Agent Development

You can extend the system by creating custom agents:

1. Inherit from `BaseAgent` in `src/repomesh/agents/base.py`
2. Implement `process_task()` and `get_capabilities()`
3. Register the agent in `AgentRegistry`
4. Add corresponding MCP tool in `mcp_server.py`

### Context Sharing

Agents automatically share findings through the `SharedContextManager`:

- API contracts are stored and searchable
- Schema changes are tracked across repositories
- Architectural decisions are preserved
- Cross-repository dependencies are identified

### Event System

All agent activities are logged through the `EventBus`:

- `AGENT_STARTED`: Agent begins processing
- `AGENT_COMPLETED`: Agent finishes successfully
- `AGENT_FAILED`: Agent encounters an error
- `CONTEXT_UPDATED`: Shared context is modified

## Troubleshooting

### Issue: "Import mcp.server.fastmcp could not be resolved"

**Solution:** Install the correct MCP package:
```bash
pip install mcp
```

### Issue: "OpenAI API key not configured"

**Solution:** Edit `.env` file and set your API key:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### Issue: "Repository cloning fails"

**Solution:** Check:
- Git is installed and accessible
- Repository URL is correct
- You have network access
- Sufficient disk space in `./repos` directory

### Issue: "Agent analysis returns empty results"

**Solution:** 
- Ensure repository has been properly scanned
- Check repository type matches agent capabilities
- Review logs for specific errors

## Performance Considerations

- **Large Repositories**: Analysis time scales with repository size
- **Concurrent Analysis**: Multiple repositories can be analyzed in parallel
- **Context Search**: Vector search is optimized for semantic similarity
- **Caching**: Repository metadata is cached after initial scan

## Security Notes

- API keys are stored in `.env` (never commit this file)
- Cloned repositories are stored locally in `./repos`
- No data is sent to external services except OpenAI API
- Context data is stored locally in ChromaDB

## Next Steps

1. **Add More Agents**: Implement DevOps, Testing, Security agents
2. **Enhanced Analysis**: Add LLM-powered deep code analysis
3. **Visualization**: Create dashboards for analysis results
4. **CI/CD Integration**: Automate analysis in build pipelines
5. **Multi-Language Support**: Extend beyond current language support

## Support

For issues or questions:
- Check the logs in `./traces` directory
- Review the `ARCHITECTURE.md` for system design
- See `TECHNICAL_SPEC.md` for implementation details

---

**Made with Bob** 🤖