# RepoMesh AI - MCP Server Setup

## 🎯 Overview

RepoMesh has been successfully restructured as an **MCP (Model Context Protocol) Server**, exposing its multi-agent repository analysis capabilities as tools that can be used by AI assistants like Claude, GPT-4, and other LLM-based applications.

## 🏗️ Architecture Changes

### What Changed

1. **MCP Server Implementation** (`src/repomesh/mcp_server.py`)
   - Converted agent system to MCP tools
   - Added 11 comprehensive tools for repository analysis
   - Exposed orchestration workflow as MCP tool
   - Integrated context management tools

2. **Agent Capabilities as Tools**
   - `analyze_frontend`: Frontend-specific analysis
   - `analyze_backend`: Backend-specific analysis
   - `run_full_analysis`: Multi-agent orchestration
   - `search_shared_context`: Cross-repository insights

3. **Repository Management**
   - `register_repository`: Clone and register repos
   - `load_local_repository`: Load existing repos
   - `list_repositories`: View all registered repos
   - `get_repository_details`: Detailed repo info

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure API Key

Edit `.env` file and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 3. Test the Setup

```bash
python test_mcp_server.py
```

This will verify:
- ✓ All imports work correctly
- ✓ Services initialize properly
- ✓ Agent registry is functional
- ✓ MCP server loads successfully
- ✓ API key is configured

### 4. Start the MCP Server

```bash
python start_mcp_server.py
```

Or directly:

```bash
python -m repomesh.mcp_server
```

## 📋 Available MCP Tools

### Repository Management (4 tools)
1. **register_repository** - Clone and register a Git repository
2. **load_local_repository** - Load an existing local repository
3. **list_repositories** - List all registered repositories
4. **get_repository_details** - Get detailed repository information

### Agent Analysis (5 tools)
5. **analyze_frontend** - Run frontend agent analysis
6. **analyze_backend** - Run backend agent analysis
7. **run_full_analysis** - Run complete multi-agent orchestration
8. **get_agent_capabilities** - Get agent capabilities
9. **list_available_agents** - List all available agents

### Context Management (2 tools)
10. **search_shared_context** - Search across agent findings
11. **store_architecture_note** - Store architectural decisions

## 🔧 Usage Examples

### Example 1: Analyze a Repository

```python
# Register a repository
result = await register_repository(
    url="https://github.com/facebook/react.git"
)

# Parse the result
import json
repo_data = json.loads(result)
repo_id = repo_data["repo_id"]

# Run frontend analysis
analysis = await analyze_frontend(repo_id=repo_id)
print(json.loads(analysis))
```

### Example 2: Multi-Repository Analysis

```python
# Register multiple repositories
frontend = await register_repository(
    url="https://github.com/user/frontend.git"
)
backend = await register_repository(
    url="https://github.com/user/backend.git"
)

# Get repo IDs
frontend_id = json.loads(frontend)["repo_id"]
backend_id = json.loads(backend)["repo_id"]

# Run orchestrated analysis
result = await run_full_analysis(
    repo_ids=f"{frontend_id},{backend_id}"
)

# View results
orchestration = json.loads(result)
print(f"Completed {orchestration['orchestration']['completed_tasks']} tasks")
print(f"Execution time: {orchestration['orchestration']['execution_time_seconds']}s")
```

### Example 3: Search Shared Context

```python
# Search for API-related information
context = await search_shared_context(
    query="REST API endpoints",
    top_k=5
)

results = json.loads(context)
for item in results["results"]:
    print(f"Repo: {item['repo_id']}")
    print(f"Agent: {item['agent_type']}")
    print(f"Content: {item['content']}\n")
```

## 🔌 Integration with Bob AI Assistant

### Bob VS Code Extension Configuration

The MCP server is already configured for Bob AI assistant! The configuration is in [`.vscode/settings.json`](.vscode/settings.json:1):

```json
{
  "bob.mcpServers": {
    "repomesh": {
      "command": "python",
      "args": [
        "${workspaceFolder}/start_mcp_server.py"
      ],
      "env": {
        "PYTHONPATH": "${workspaceFolder}/src"
      }
    }
  }
}
```

### How to Use with Bob

1. **Reload VS Code** to apply the MCP server configuration
2. **Open Bob** in VS Code (the AI assistant you're currently using)
3. **Use the MCP tools** by asking Bob to:
   - "Register a repository from GitHub"
   - "Analyze the frontend of a repository"
   - "Run a full analysis on multiple repositories"
   - "Search for API endpoints in the shared context"

### Example Bob Commands

```
"Use the register_repository tool to clone https://github.com/facebook/react"

"Use the analyze_frontend tool on the repository we just registered"

"Use the search_shared_context tool to find all API endpoints"

"Use the run_full_analysis tool to analyze all registered repositories"
```

### Using with Other MCP Clients

The server uses stdio transport and follows the MCP specification, making it compatible with any MCP client including Claude Desktop, GPT-4, and other LLM-based tools.

## 📊 What Each Agent Analyzes

### Frontend Agent
- **Components**: React, Vue, Svelte, Angular components
- **UI Patterns**: Material-UI, Tailwind CSS, Bootstrap, etc.
- **API Integrations**: Axios, Fetch API, Apollo GraphQL, React Query
- **State Management**: Redux, MobX, Zustand patterns

### Backend Agent
- **API Endpoints**: REST, GraphQL endpoints
- **Frameworks**: FastAPI, Flask, Django, Express, NestJS, Spring
- **Database Schemas**: Migrations, ORM models
- **Service Dependencies**: PostgreSQL, MongoDB, Redis, RabbitMQ, Kafka

### Orchestration Workflow
- Coordinates multiple agents
- Shares context between agents
- Parallel execution where possible
- Tracks execution metrics

## 🗂️ Project Structure

```
MultiMind/
├── src/repomesh/
│   ├── mcp_server.py          # ⭐ Main MCP server (restructured)
│   ├── agents/
│   │   ├── base.py            # Base agent class
│   │   ├── frontend.py        # Frontend agent
│   │   ├── backend.py         # Backend agent
│   │   └── registry.py        # Agent registry
│   ├── orchestrator/
│   │   └── workflow.py        # LangGraph orchestration
│   ├── context/
│   │   ├── manager.py         # Context manager
│   │   └── store.py           # Vector store
│   └── repos/
│       └── manager.py         # Repository manager
├── start_mcp_server.py        # ⭐ Server startup script
├── test_mcp_server.py         # ⭐ Test suite
├── MCP_SERVER_GUIDE.md        # ⭐ Detailed guide
├── .env                       # ⭐ Configuration (with your API key)
└── requirements.txt           # Dependencies
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python test_mcp_server.py
```

Expected output:
```
======================================================================
RepoMesh MCP Server - Test Suite
======================================================================
Testing imports...
✓ All core imports successful

Testing service initialization...
✓ All services initialized successfully

Testing agent registry...
  Registered agents: ['frontend', 'backend']
  frontend capabilities: ['component_analysis', 'ui_pattern_detection', ...]
  backend capabilities: ['api_endpoint_extraction', 'schema_tracking', ...]
✓ Agent registry working correctly

Testing MCP server...
✓ MCP server module loaded successfully

Checking API key configuration...
✓ OpenAI API key configured

======================================================================
Test Results Summary
======================================================================
✓ PASS: Imports
✓ PASS: Initialization
✓ PASS: Agent Registry
✓ PASS: MCP Server
✓ PASS: API Key
======================================================================
✓ All critical tests passed!
```

## 📚 Documentation

- **[MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md)** - Comprehensive usage guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[TECHNICAL_SPEC.md](TECHNICAL_SPEC.md)** - Technical specifications

## 🔍 Troubleshooting

### Issue: Import errors

**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "OpenAI API key not configured"

**Solution:** Edit `.env` and set your API key:
```bash
OPENAI_API_KEY=sk-your-actual-key-here
```

### Issue: MCP server won't start

**Solution:** Run the test suite first:
```bash
python test_mcp_server.py
```

### Issue: Repository cloning fails

**Solution:** Ensure:
- Git is installed
- Network connectivity
- Sufficient disk space in `./repos`

## 🎯 Next Steps

1. **Start the Server**: `python start_mcp_server.py`
2. **Register a Repository**: Use `register_repository` tool
3. **Run Analysis**: Use `analyze_frontend` or `analyze_backend`
4. **Explore Context**: Use `search_shared_context` to find insights

## 🤝 Contributing

To add new agents:

1. Create agent class in `src/repomesh/agents/`
2. Inherit from `BaseAgent`
3. Implement `process_task()` and `get_capabilities()`
4. Register in `AgentRegistry`
5. Add MCP tool in `mcp_server.py`

## 📝 Notes

- All repository data is stored locally in `./repos`
- Context data is stored in `./data/chroma`
- Logs are available in `./traces`
- The server uses stdio transport for MCP communication

## ✅ Summary

✅ **Agent system converted to MCP server**
✅ **11 comprehensive MCP tools available**
✅ **Multi-agent orchestration exposed**
✅ **Context sharing between agents**
✅ **Ready for AI assistant integration**
✅ **Test suite included**
✅ **Comprehensive documentation**

---

**Made with Bob** 🤖

For detailed usage instructions, see [MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md)