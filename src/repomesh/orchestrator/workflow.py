"""
LangGraph orchestration workflow for multi-agent coordination.

This module implements the LangGraph workflow that coordinates multiple agents
to analyze repositories in a structured, stateful manner.
"""

from datetime import datetime
from typing import Any, Dict, List
from uuid import UUID

from langgraph.graph import END, StateGraph

from repomesh.agents.registry import AgentRegistry
from repomesh.core.events import EventBus
from repomesh.core.models import AgentType, RepoMetadata, Task, TaskStatus
from repomesh.core.types import OrchestrationState
from repomesh.context.manager import SharedContextManager
from repomesh.repos.manager import RepoManager


class OrchestrationWorkflow:
    """LangGraph workflow for orchestrating multi-agent analysis."""

    def __init__(
        self,
        repo_manager: RepoManager,
        agent_registry: AgentRegistry,
        context_manager: SharedContextManager,
        event_bus: EventBus,
        max_steps: int = 50,
    ) -> None:
        """Initialize the orchestration workflow.

        Args:
            repo_manager: Repository manager
            agent_registry: Agent registry
            context_manager: Shared context manager
            event_bus: Event bus
            max_steps: Maximum orchestration steps
        """
        self.repo_manager = repo_manager
        self.agent_registry = agent_registry
        self.context_manager = context_manager
        self.event_bus = event_bus
        self.max_steps = max_steps
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph state graph.

        Returns:
            Configured state graph
        """
        # Create state graph
        workflow = StateGraph(OrchestrationState)

        # Add nodes
        workflow.add_node("planner", self._planner_node)
        workflow.add_node("task_distributor", self._task_distributor_node)
        workflow.add_node("frontend_agent", self._frontend_agent_node)
        workflow.add_node("backend_agent", self._backend_agent_node)
        workflow.add_node("context_sync", self._context_sync_node)

        # Set entry point
        workflow.set_entry_point("planner")

        # Add edges
        workflow.add_edge("planner", "task_distributor")
        workflow.add_edge("task_distributor", "frontend_agent")
        workflow.add_edge("task_distributor", "backend_agent")
        workflow.add_edge("frontend_agent", "context_sync")
        workflow.add_edge("backend_agent", "context_sync")

        # Add conditional edge from context_sync
        workflow.add_conditional_edges(
            "context_sync",
            self._should_continue,
            {
                "continue": "task_distributor",
                "end": END,
            },
        )

        return workflow.compile()

    async def _planner_node(self, state: OrchestrationState) -> OrchestrationState:
        """Planning node: Analyze repositories and create tasks.

        Args:
            state: Current orchestration state

        Returns:
            Updated state
        """
        # Initialize state if needed
        if "current_step" not in state:
            state["current_step"] = 0
            state["max_steps"] = self.max_steps
            state["should_continue"] = True
            state["started_at"] = datetime.utcnow().isoformat()
            state["tasks"] = []
            state["pending_tasks"] = []
            state["in_progress_tasks"] = []
            state["completed_tasks"] = []
            state["failed_tasks"] = []
            state["agent_assignments"] = {}
            state["agent_results"] = {}
            state["shared_context"] = {}
            state["context_updates"] = []

        # Get repository metadata
        repo_metadata_dict = {}
        for repo_id in state.get("repo_ids", []):
            try:
                metadata = self.repo_manager.get_repo_metadata(repo_id)
                repo_metadata_dict[repo_id] = {
                    "name": metadata.name,
                    "type": metadata.repo_type.value,
                    "tech_stack": metadata.tech_stack,
                    "file_count": metadata.file_count,
                }
            except Exception:
                continue

        state["repo_metadata"] = repo_metadata_dict

        # Create tasks for each repository
        tasks: List[Task] = []
        for repo_id in state.get("repo_ids", []):
            metadata = self.repo_manager.get_repo_metadata(repo_id)

            # Determine which agents to use based on repo type
            agent_types = self.agent_registry.find_agents_for_repo_type(
                metadata.repo_type.value
            )

            # Create tasks for each agent
            for agent_type in agent_types:
                task = Task(
                    repo_id=repo_id,
                    agent_type=agent_type,
                    description=f"Analyze {metadata.name} with {agent_type.value} agent",
                    priority=5,
                    result=None,
                    error=None,
                    started_at=None,
                    completed_at=None,
                )
                tasks.append(task)

        state["tasks"] = tasks
        state["pending_tasks"] = tasks.copy()

        return state

    async def _task_distributor_node(self, state: OrchestrationState) -> OrchestrationState:
        """Task distribution node: Assign tasks to agents.

        Args:
            state: Current orchestration state

        Returns:
            Updated state
        """
        state["current_step"] = state.get("current_step", 0) + 1

        # Group pending tasks by agent type
        agent_assignments: Dict[AgentType, List[UUID]] = {}
        
        for task in state.get("pending_tasks", []):
            if task.agent_type not in agent_assignments:
                agent_assignments[task.agent_type] = []
            agent_assignments[task.agent_type].append(task.id)

        state["agent_assignments"] = agent_assignments

        # Move tasks to in_progress
        state["in_progress_tasks"] = state.get("pending_tasks", [])
        state["pending_tasks"] = []

        return state

    async def _frontend_agent_node(self, state: OrchestrationState) -> OrchestrationState:
        """Frontend agent node: Execute frontend tasks.

        Args:
            state: Current orchestration state

        Returns:
            Updated state
        """
        agent = self.agent_registry.get_agent(AgentType.FRONTEND)
        
        # Get tasks assigned to frontend agent
        frontend_task_ids = state.get("agent_assignments", {}).get(AgentType.FRONTEND, [])
        
        for task in state.get("in_progress_tasks", []):
            if task.id in frontend_task_ids and task.status == TaskStatus.PENDING:
                try:
                    # Get repository metadata
                    metadata = self.repo_manager.get_repo_metadata(task.repo_id)
                    
                    # Execute task
                    task.start()
                    result = await agent.process_task(task, metadata)
                    task.complete(result)
                    
                    # Store result
                    state["agent_results"][task.id] = result
                    
                    # Move to completed
                    state["completed_tasks"].append(task)
                    
                except Exception as e:
                    task.fail(str(e))
                    state["failed_tasks"].append(task)

        # Remove completed/failed tasks from in_progress
        state["in_progress_tasks"] = [
            t for t in state.get("in_progress_tasks", [])
            if t.status == TaskStatus.IN_PROGRESS
        ]

        return state

    async def _backend_agent_node(self, state: OrchestrationState) -> OrchestrationState:
        """Backend agent node: Execute backend tasks.

        Args:
            state: Current orchestration state

        Returns:
            Updated state
        """
        agent = self.agent_registry.get_agent(AgentType.BACKEND)
        
        # Get tasks assigned to backend agent
        backend_task_ids = state.get("agent_assignments", {}).get(AgentType.BACKEND, [])
        
        for task in state.get("in_progress_tasks", []):
            if task.id in backend_task_ids and task.status == TaskStatus.PENDING:
                try:
                    # Get repository metadata
                    metadata = self.repo_manager.get_repo_metadata(task.repo_id)
                    
                    # Execute task
                    task.start()
                    result = await agent.process_task(task, metadata)
                    task.complete(result)
                    
                    # Store result
                    state["agent_results"][task.id] = result
                    
                    # Move to completed
                    state["completed_tasks"].append(task)
                    
                except Exception as e:
                    task.fail(str(e))
                    state["failed_tasks"].append(task)

        # Remove completed/failed tasks from in_progress
        state["in_progress_tasks"] = [
            t for t in state.get("in_progress_tasks", [])
            if t.status == TaskStatus.IN_PROGRESS
        ]

        return state

    async def _context_sync_node(self, state: OrchestrationState) -> OrchestrationState:
        """Context synchronization node: Sync context between agents.

        Args:
            state: Current orchestration state

        Returns:
            Updated state
        """
        # Collect context updates from completed tasks
        context_updates = []
        
        for task in state.get("completed_tasks", []):
            if task.id in state.get("agent_results", {}):
                result = state["agent_results"][task.id]
                context_updates.append({
                    "task_id": str(task.id),
                    "agent_type": task.agent_type.value,
                    "repo_id": str(task.repo_id),
                    "result": result,
                })

        state["context_updates"] = context_updates

        # Update shared context
        for update in context_updates:
            state["shared_context"][update["task_id"]] = update

        return state

    def _should_continue(self, state: OrchestrationState) -> str:
        """Determine if orchestration should continue.

        Args:
            state: Current orchestration state

        Returns:
            "continue" or "end"
        """
        # Check if max steps reached
        if state.get("current_step", 0) >= state.get("max_steps", self.max_steps):
            return "end"

        # Check if there are pending tasks
        if state.get("pending_tasks", []):
            return "continue"

        # Check if there are in-progress tasks
        if state.get("in_progress_tasks", []):
            return "continue"

        # All tasks completed
        return "end"

    async def run(self, repo_ids: List[UUID]) -> Dict[str, Any]:
        """Run the orchestration workflow.

        Args:
            repo_ids: List of repository IDs to analyze

        Returns:
            Orchestration results
        """
        # Initialize state
        initial_state: OrchestrationState = {
            "repo_ids": repo_ids,
            "repo_metadata": {},
            "tasks": [],
            "pending_tasks": [],
            "in_progress_tasks": [],
            "completed_tasks": [],
            "failed_tasks": [],
            "agent_assignments": {},
            "agent_results": {},
            "shared_context": {},
            "context_updates": [],
            "current_step": 0,
            "max_steps": self.max_steps,
            "should_continue": True,
            "error": None,
            "started_at": datetime.utcnow().isoformat(),
            "completed_at": None,
            "execution_time_seconds": None,
        }

        # Run workflow
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            # Calculate execution time
            started_at = datetime.fromisoformat(final_state["started_at"])
            completed_at = datetime.utcnow()
            execution_time = (completed_at - started_at).total_seconds()
            
            final_state["completed_at"] = completed_at.isoformat()
            final_state["execution_time_seconds"] = execution_time

            return final_state

        except Exception as e:
            return {
                **initial_state,
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat(),
            }

# Made with Bob
