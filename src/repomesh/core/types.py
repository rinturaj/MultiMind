"""
Type definitions for RepoMesh AI.

This module defines TypedDicts and other type aliases used throughout the system.
"""

from typing import Any, Dict, List, TypedDict
from uuid import UUID

from repomesh.core.models import AgentType, Task


class OrchestrationState(TypedDict, total=False):
    """State object passed through the LangGraph orchestration workflow.
    
    This TypedDict defines the structure of the state that flows through
    the orchestration graph, containing all information needed for
    multi-agent coordination.
    """

    # Repository information
    repo_ids: List[UUID]
    repo_metadata: Dict[UUID, Dict[str, Any]]
    
    # Task management
    tasks: List[Task]
    pending_tasks: List[Task]
    in_progress_tasks: List[Task]
    completed_tasks: List[Task]
    failed_tasks: List[Task]
    
    # Agent coordination
    agent_assignments: Dict[AgentType, List[UUID]]  # agent_type -> task_ids
    agent_results: Dict[UUID, Dict[str, Any]]  # task_id -> result
    
    # Context and communication
    shared_context: Dict[str, Any]
    context_updates: List[Dict[str, Any]]
    
    # Orchestration control
    current_step: int
    max_steps: int
    should_continue: bool
    error: str | None
    
    # Execution metadata
    started_at: str
    completed_at: str | None
    execution_time_seconds: float | None


class AgentCapabilities(TypedDict):
    """Capabilities of an agent."""
    
    agent_type: AgentType
    supported_repo_types: List[str]
    supported_tasks: List[str]
    max_concurrent_tasks: int
    requires_llm: bool


class ContextSearchResult(TypedDict):
    """Result from context search."""
    
    key: str
    content: str
    similarity: float
    metadata: Dict[str, Any]


class RepoSummary(TypedDict):
    """Summary of repository analysis."""
    
    repo_id: UUID
    name: str
    repo_type: str
    tech_stack: List[str]
    file_count: int
    code_file_count: int
    total_lines: int
    summary: str

# Made with Bob
