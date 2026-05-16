# Test Bob Integration

## Quick Test Commands

After reloading VS Code, try these commands with Bob to test the MCP integration:

### Test 1: Check Available Tools
```
What MCP tools do you have available?
```

**Expected:** Bob should list 11 RepoMesh tools

### Test 2: List Repositories (Empty State)
```
Use the list_repositories tool
```

**Expected:** Should return "No repositories registered yet"

### Test 3: Register a Small Repository
```
Use the register_repository tool to clone https://github.com/octocat/Hello-World
```

**Expected:** Should return success with repo_id and metadata

### Test 4: List Repositories Again
```
Use the list_repositories tool
```

**Expected:** Should show the Hello-World repository

### Test 5: Get Repository Details
```
Use the get_repository_details tool with the repo_id from the previous result
```

**Expected:** Should return detailed metadata about Hello-World repo

### Test 6: List Available Agents
```
Use the list_available_agents tool
```

**Expected:** Should show frontend and backend agents with their capabilities

### Test 7: Get Agent Capabilities
```
Use the get_agent_capabilities tool for the frontend agent
```

**Expected:** Should return frontend agent capabilities

## Full Integration Test

Try this complete workflow:

```
1. Register a repository: https://github.com/octocat/Hello-World
2. List all repositories to confirm it's registered
3. Get the repository details
4. List available agents
5. Try to analyze it with the frontend agent (may not find much in Hello-World)
```

## Troubleshooting

If Bob says the tools are not available:

1. **Reload VS Code**: Press Ctrl+Shift+P → "Reload Window"
2. **Check settings.json**: Verify `.vscode/settings.json` exists with the MCP configuration
3. **Check Python**: Run `python --version` in terminal
4. **Check dependencies**: Run `pip install -r requirements.txt`
5. **Check .env**: Verify your OpenAI API key is set

## Success Indicators

✅ Bob can see the MCP tools
✅ Bob can list repositories
✅ Bob can register a repository
✅ Bob can get repository details
✅ Bob can list agents
✅ Bob can run analysis tools

If all these work, the integration is successful! 🎉