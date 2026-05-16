# Bob AI Assistant Integration Guide

## 🤖 Overview

RepoMesh MCP Server is now integrated with **Bob AI Assistant** (the VS Code extension you're currently using). This allows Bob to use the multi-agent repository analysis system directly within VS Code.

## ✅ Configuration Complete

The MCP server is already configured in [`.vscode/settings.json`](.vscode/settings.json:1):

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

## 🚀 How to Use

### Step 1: Reload VS Code

After the configuration is added, reload VS Code to activate the MCP server:

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac)
2. Type "Reload Window"
3. Press Enter

### Step 2: Verify Bob Can See the Tools

Ask Bob:
```
"What MCP tools do you have available?"
```

Bob should list the 11 RepoMesh tools:
- register_repository
- load_local_repository
- list_repositories
- get_repository_details
- analyze_frontend
- analyze_backend
- run_full_analysis
- search_shared_context
- store_architecture_note
- get_agent_capabilities
- list_available_agents

### Step 3: Start Using the Tools

You can now ask Bob to use these tools naturally!

## 📋 Example Commands for Bob

### Register a Repository

```
"Use the register_repository tool to clone https://github.com/facebook/react"
```

or more naturally:

```
"Register the React repository from GitHub"
```

### Analyze a Repository

```
"Use the analyze_frontend tool on the repository we just registered"
```

or:

```
"Analyze the frontend of the React repository"
```

### List Repositories

```
"Use the list_repositories tool to show me all registered repos"
```

or:

```
"Show me all the repositories in the mesh"
```

### Search Context

```
"Use the search_shared_context tool to find API endpoints"
```

or:

```
"Search for all API endpoints across repositories"
```

### Full Multi-Agent Analysis

```
"Use the run_full_analysis tool on all registered repositories"
```

or:

```
"Run a complete analysis on all my repositories"
```

## 🎯 Complete Workflow Example

Here's a complete workflow you can try with Bob:

### 1. Register Two Repositories

```
"Register these two repositories:
1. https://github.com/vercel/next.js (frontend)
2. https://github.com/fastapi/fastapi (backend)"
```

### 2. List Them

```
"List all registered repositories"
```

### 3. Analyze Frontend

```
"Analyze the frontend of the Next.js repository"
```

### 4. Analyze Backend

```
"Analyze the backend of the FastAPI repository"
```

### 5. Search for Patterns

```
"Search the shared context for React components"
```

### 6. Run Full Orchestration

```
"Run a full multi-agent analysis on both repositories"
```

## 🔧 Advanced Usage

### Store Architecture Notes

```
"Store an architecture note for the Next.js repository:
'Using App Router with Server Components for better performance'"
```

### Get Agent Capabilities

```
"What are the capabilities of the frontend agent?"
```

### Search Specific Repository

```
"Search for API endpoints in the FastAPI repository only"
```

## 🐛 Troubleshooting

### Issue: Bob says "MCP server not available"

**Solution:**
1. Ensure VS Code is reloaded after adding the configuration
2. Check that Python is in your PATH
3. Verify `.env` file has your OpenAI API key

### Issue: "Python command not found"

**Solution:**
Update `.vscode/settings.json` to use full Python path:
```json
{
  "bob.mcpServers": {
    "repomesh": {
      "command": "C:/Users/YourName/AppData/Local/Programs/Python/Python311/python.exe",
      "args": ["${workspaceFolder}/start_mcp_server.py"]
    }
  }
}
```

### Issue: "Module not found" errors

**Solution:**
1. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```
2. Check that PYTHONPATH is set correctly in settings.json

### Issue: Tools work but analysis fails

**Solution:**
1. Verify OpenAI API key in `.env` file
2. Check you have sufficient API credits
3. Review logs in `./traces` directory

## 📊 What Bob Can Do with These Tools

### Repository Management
- ✅ Clone and register Git repositories
- ✅ Load existing local repositories
- ✅ List all registered repositories
- ✅ Get detailed repository information

### Code Analysis
- ✅ Analyze frontend codebases (React, Vue, Angular, etc.)
- ✅ Analyze backend codebases (FastAPI, Django, Express, etc.)
- ✅ Detect UI patterns and libraries
- ✅ Extract API endpoints and schemas
- ✅ Map service dependencies

### Multi-Agent Orchestration
- ✅ Coordinate multiple agents
- ✅ Share context between agents
- ✅ Parallel analysis execution
- ✅ Track execution metrics

### Context Management
- ✅ Search across all repositories
- ✅ Find API contracts
- ✅ Locate schema definitions
- ✅ Store architectural decisions

## 🎨 Natural Language Examples

Bob understands natural language, so you can ask things like:

```
"I want to analyze a React project from GitHub"

"Show me all the API endpoints in my backend repositories"

"What UI libraries are being used across all my frontend projects?"

"Store a note that we're migrating from REST to GraphQL"

"Find all database schemas in the registered repositories"

"Run a complete analysis on my microservices"
```

## 🔄 Workflow Integration

### During Code Review

```
"Register the PR's repository and analyze it for frontend best practices"
```

### During Architecture Planning

```
"Search for similar API patterns in our other services"
```

### During Refactoring

```
"Analyze the current structure and suggest improvements"
```

### During Onboarding

```
"Give me an overview of all our repositories and their tech stacks"
```

## 📈 Performance Tips

1. **Register repositories once** - They stay in the system
2. **Use specific queries** - More targeted searches are faster
3. **Analyze incrementally** - Start with one agent, then orchestrate
4. **Store important findings** - Use architecture notes for key decisions

## 🎓 Learning Resources

- **[README_MCP_SERVER.md](README_MCP_SERVER.md)** - Quick start guide
- **[MCP_SERVER_GUIDE.md](MCP_SERVER_GUIDE.md)** - Detailed tool documentation
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[test_mcp_server.py](test_mcp_server.py)** - Test examples

## ✨ Pro Tips

1. **Chain operations**: "Register the repo, then analyze it, then search for patterns"
2. **Be specific**: Include repository names or IDs in your requests
3. **Use context**: Bob remembers previous operations in the conversation
4. **Explore results**: Ask Bob to explain or summarize the analysis results

## 🎉 You're Ready!

The MCP server is configured and ready to use with Bob. Just reload VS Code and start asking Bob to analyze your repositories!

Try this first command:
```
"List all available MCP tools and explain what each one does"
```

---

**Made with Bob** 🤖