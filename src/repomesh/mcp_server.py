"""
MCP Server implementation for RepoMesh AI.

This module exposes the multi-agent repository analysis system as MCP tools,
allowing AI assistants to analyze codebases using specialized agents.
"""

import asyncio
import json
from uuid import UUID
from typing import Optional, List, Dict, Any

from fastmcp import FastMCP

from repomesh.agents.registry import AgentRegistry
from repomesh.context.manager import SharedContextManager
from repomesh.context.store import InMemoryStore
from repomesh.core.events import EventBus
from repomesh.orchestrator.workflow import OrchestrationWorkflow
from repomesh.repos.manager import RepoManager
from repomesh.core.models import AgentType, RepoType, Task

# Initialize services
repo_manager = RepoManager()
event_bus = EventBus()
context_store = InMemoryStore()
context_manager = SharedContextManager(context_store, event_bus)
agent_registry = AgentRegistry(context_manager, event_bus)
orchestrator = OrchestrationWorkflow(
    repo_manager=repo_manager,
    agent_registry=agent_registry,
    context_manager=context_manager,
    event_bus=event_bus,
)

# Initialize FastMCP Server
mcp = FastMCP("RepoMesh AI - Multi-Agent Repository Analysis")


# ============================================================================
# Repository Management Tools
# ============================================================================

@mcp.tool()
async def register_repository(url: str, name: Optional[str] = None) -> str:
    """Register and clone a new repository into the mesh for analysis.
    
    Args:
        url: Git repository URL (e.g., https://github.com/user/repo.git)
        name: Optional custom name for the repository
    
    Returns:
        Success message with repository ID and metadata
    """
    try:
        repo = repo_manager.clone_repo(url, name)
        return json.dumps({
            "success": True,
            "message": f"Successfully registered repository: {repo.name}",
            "repo_id": str(repo.id),
            "name": repo.name,
            "type": repo.repo_type.value,
            "tech_stack": repo.tech_stack,
            "file_count": repo.file_count,
            "code_file_count": repo.code_file_count,
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to register repository: {str(e)}"
        }, indent=2)


@mcp.tool()
async def load_local_repository(path: str, url: Optional[str] = None) -> str:
    """Load an existing local repository into the mesh for analysis.
    
    Args:
        path: Local path to the repository
        url: Optional remote URL for reference
    
    Returns:
        Success message with repository ID and metadata
    """
    try:
        repo = repo_manager.load_local_repo(path, url)
        return json.dumps({
            "success": True,
            "message": f"Successfully loaded repository: {repo.name}",
            "repo_id": str(repo.id),
            "name": repo.name,
            "type": repo.repo_type.value,
            "tech_stack": repo.tech_stack,
            "file_count": repo.file_count,
            "code_file_count": repo.code_file_count,
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to load repository: {str(e)}"
        }, indent=2)


@mcp.tool()
async def list_repositories() -> str:
    """List all registered repositories in the mesh.
    
    Returns:
        JSON list of all repositories with their metadata
    """
    repos = repo_manager.list_repos()
    if not repos:
        return json.dumps({
            "success": True,
            "count": 0,
            "message": "No repositories registered yet.",
            "repositories": []
        }, indent=2)
    
    repo_list = []
    for r in repos:
        repo_list.append({
            "id": str(r.id),
            "name": r.name,
            "path": r.path,
            "type": r.repo_type.value,
            "tech_stack": r.tech_stack,
            "file_count": r.file_count,
            "code_file_count": r.code_file_count,
        })
    
    return json.dumps({
        "success": True,
        "count": len(repo_list),
        "repositories": repo_list
    }, indent=2)


@mcp.tool()
async def get_repository_details(repo_id: str) -> str:
    """Get detailed information about a specific repository.
    
    Args:
        repo_id: UUID of the repository
    
    Returns:
        Detailed repository metadata including dependencies and file structure
    """
    try:
        uuid_obj = UUID(repo_id)
        metadata = repo_manager.get_repo_metadata(uuid_obj)
        
        return json.dumps({
            "success": True,
            "repository": {
                "id": str(metadata.id),
                "name": metadata.name,
                "path": metadata.path,
                "url": metadata.url,
                "type": metadata.repo_type.value,
                "tech_stack": metadata.tech_stack,
                "dependencies": metadata.dependencies,
                "file_count": metadata.file_count,
                "code_file_count": metadata.code_file_count,
                "total_lines": metadata.total_lines,
            }
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to get repository details: {str(e)}"
        }, indent=2)


# ============================================================================
# Agent Analysis Tools
# ============================================================================

@mcp.tool()
async def analyze_frontend(repo_id: str) -> str:
    """Analyze a repository using the Frontend Agent.
    
    Detects and analyzes:
    - UI components (React, Vue, Svelte, etc.)
    - UI patterns and libraries (Material-UI, Tailwind, etc.)
    - API integrations and data fetching patterns
    
    Args:
        repo_id: UUID of the repository to analyze
    
    Returns:
        Frontend analysis results including components, patterns, and integrations
    """
    try:
        uuid_obj = UUID(repo_id)
        metadata = repo_manager.get_repo_metadata(uuid_obj)
        
        # Get frontend agent
        agent = agent_registry.get_agent(AgentType.FRONTEND)
        
        # Create task
        task = Task(
            repo_id=uuid_obj,
            agent_type=AgentType.FRONTEND,
            description=f"Frontend analysis of {metadata.name}",
            priority=5,
        )
        
        # Execute analysis
        result = await agent.process_task(task, metadata)
        
        return json.dumps({
            "success": True,
            "repo_name": metadata.name,
            "agent": "frontend",
            "analysis": {
                "components": result.get("components", []),
                "ui_patterns": result.get("ui_patterns", []),
                "api_integrations": result.get("api_integrations", []),
                "summary": result.get("summary", ""),
            }
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Frontend analysis failed: {str(e)}"
        }, indent=2)


@mcp.tool()
async def analyze_backend(repo_id: str) -> str:
    """Analyze a repository using the Backend Agent.
    
    Detects and analyzes:
    - API endpoints and routes
    - Database schemas and migrations
    - Service dependencies (databases, message queues, etc.)
    
    Args:
        repo_id: UUID of the repository to analyze
    
    Returns:
        Backend analysis results including endpoints, schemas, and dependencies
    """
    try:
        uuid_obj = UUID(repo_id)
        metadata = repo_manager.get_repo_metadata(uuid_obj)
        
        # Get backend agent
        agent = agent_registry.get_agent(AgentType.BACKEND)
        
        # Create task
        task = Task(
            repo_id=uuid_obj,
            agent_type=AgentType.BACKEND,
            description=f"Backend analysis of {metadata.name}",
            priority=5,
        )
        
        # Execute analysis
        result = await agent.process_task(task, metadata)
        
        return json.dumps({
            "success": True,
            "repo_name": metadata.name,
            "agent": "backend",
            "analysis": {
                "endpoints": result.get("endpoints", []),
                "schemas": result.get("schemas", []),
                "dependencies": result.get("dependencies", []),
                "summary": result.get("summary", ""),
            }
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Backend analysis failed: {str(e)}"
        }, indent=2)


@mcp.tool()
async def get_agent_capabilities(agent_type: str) -> str:
    """Get capabilities and supported features of a specific agent.
    
    Args:
        agent_type: Type of agent (frontend, backend, devops, testing, documentation, security)
    
    Returns:
        Agent capabilities including supported repo types and tasks
    """
    try:
        agent_enum = AgentType(agent_type.lower())
        capabilities = agent_registry.get_capabilities(agent_enum)
        
        return json.dumps({
            "success": True,
            "agent_type": agent_type,
            "capabilities": capabilities
        }, indent=2)
    except ValueError:
        return json.dumps({
            "success": False,
            "error": f"Invalid agent type: {agent_type}. Valid types: frontend, backend, devops, testing, documentation, security"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to get capabilities: {str(e)}"
        }, indent=2)


@mcp.tool()
async def list_available_agents() -> str:
    """List all available agents and their capabilities.
    
    Returns:
        List of all registered agents with their capabilities
    """
    try:
        all_capabilities = agent_registry.get_all_capabilities()
        
        agents_info = []
        for agent_type, capabilities in all_capabilities.items():
            agents_info.append({
                "type": agent_type.value,
                "capabilities": capabilities
            })
        
        return json.dumps({
            "success": True,
            "count": len(agents_info),
            "agents": agents_info
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to list agents: {str(e)}"
        }, indent=2)


# ============================================================================
# Orchestration Tools
# ============================================================================

@mcp.tool()
async def run_full_analysis(repo_ids: str) -> str:
    """Run a complete multi-agent analysis workflow on one or more repositories.
    
    This orchestrates all relevant agents to analyze the repositories in a coordinated manner,
    with agents sharing context and insights through the shared context manager.
    
    Args:
        repo_ids: Comma-separated list of repository UUIDs to analyze
    
    Returns:
        Complete orchestration results including all agent outputs and shared context
    """
    try:
        # Parse repo IDs
        id_list = [UUID(rid.strip()) for rid in repo_ids.split(",")]
        
        # Run orchestration
        result = await orchestrator.run(id_list)
        
        # Format results
        completed_tasks = result.get("completed_tasks", [])
        failed_tasks = result.get("failed_tasks", [])
        
        task_results = []
        for task in completed_tasks:
            task_result = result.get("agent_results", {}).get(task.id, {})
            task_results.append({
                "repo_id": str(task.repo_id),
                "agent": task.agent_type.value,
                "status": "completed",
                "result": task_result
            })
        
        for task in failed_tasks:
            task_results.append({
                "repo_id": str(task.repo_id),
                "agent": task.agent_type.value,
                "status": "failed",
                "error": task.error
            })
        
        return json.dumps({
            "success": True,
            "orchestration": {
                "total_steps": result.get("current_step", 0),
                "execution_time_seconds": result.get("execution_time_seconds", 0),
                "completed_tasks": len(completed_tasks),
                "failed_tasks": len(failed_tasks),
                "task_results": task_results,
                "shared_context_updates": len(result.get("context_updates", [])),
            }
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Orchestration failed: {str(e)}"
        }, indent=2)


# ============================================================================
# Context Management Tools
# ============================================================================

@mcp.tool()
async def search_shared_context(query: str, repo_id: Optional[str] = None, top_k: int = 10) -> str:
    """Search for API contracts, schema definitions, or architecture notes across repositories.
    
    Args:
        query: Search query for finding relevant context
        repo_id: Optional UUID to filter results to a specific repository
        top_k: Number of results to return (default: 10)
    
    Returns:
        Relevant context entries from the shared context store
    """
    try:
        repo_uuid = UUID(repo_id) if repo_id else None
        results = await context_manager.get_relevant_context(
            query=query,
            repo_id=repo_uuid,
            top_k=top_k
        )
        
        if not results:
            return json.dumps({
                "success": True,
                "count": 0,
                "message": "No relevant context found.",
                "results": []
            }, indent=2)
        
        formatted_results = []
        for r in results:
            formatted_results.append({
                "repo_id": str(r.repo_id),
                "agent_type": r.agent_type.value if r.agent_type else "unknown",
                "key": r.key,
                "content": r.content,
                "metadata": r.metadata,
            })
        
        return json.dumps({
            "success": True,
            "count": len(formatted_results),
            "query": query,
            "results": formatted_results
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Context search failed: {str(e)}"
        }, indent=2)


@mcp.tool()
async def store_architecture_note(content: str, repo_id: str, agent_type: str = "backend") -> str:
    """Store an architectural decision or note for other agents to reference.
    
    Args:
        content: The architectural note or decision content
        repo_id: UUID of the repository this note applies to
        agent_type: Agent type storing the note (default: backend)
    
    Returns:
        Confirmation with the stored entry key
    """
    try:
        uuid_obj = UUID(repo_id)
        agent_enum = AgentType(agent_type.lower())
        
        entry = await context_manager.store_architecture_note(
            content=content,
            repo_id=uuid_obj,
            agent_type=agent_enum
        )
        
        return json.dumps({
            "success": True,
            "message": "Architecture note stored successfully",
            "entry_key": entry.key,
            "repo_id": str(entry.repo_id),
            "agent_type": entry.agent_type.value if entry.agent_type else "unknown",
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Failed to store note: {str(e)}"
        }, indent=2)


# ============================================================================
# Resource Endpoints
# ============================================================================

@mcp.resource("repomesh://repos/list")
def list_repositories_resource() -> str:
    """Resource endpoint for listing all repositories."""
    repos = repo_manager.list_repos()
    if not repos:
        return "No repositories registered yet."
    
    formatted_repos = []
    for r in repos:
        formatted_repos.append(
            f"Name: {r.name}\n"
            f"ID: {r.id}\n"
            f"Path: {r.path}\n"
            f"Type: {r.repo_type.value}\n"
            f"Tech Stack: {', '.join(r.tech_stack)}\n"
        )
    return "\n---\n".join(formatted_repos)


@mcp.resource("repomesh://agents/list")
def list_agents_resource() -> str:
    """Resource endpoint for listing all available agents."""
    agent_types = agent_registry.list_agents()
    
    formatted_agents = []
    for agent_type in agent_types:
        capabilities = agent_registry.get_capabilities(agent_type)
        formatted_agents.append(
            f"Agent: {agent_type.value}\n"
            f"Supported Repo Types: {', '.join(capabilities.get('supported_repo_types', []))}\n"
            f"Supported Tasks: {', '.join(capabilities.get('supported_tasks', []))}\n"
        )
    
    return "\n---\n".join(formatted_agents)


# ============================================================================
# Server Entry Point
# ============================================================================

if __name__ == "__main__":
    # Run the MCP server with stdio transport
    mcp.run(transport='stdio')

# Made with Bob
