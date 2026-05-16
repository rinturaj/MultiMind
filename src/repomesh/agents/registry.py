"""
Agent registry for managing and discovering agents.

This module provides a registry for registering agents and discovering
their capabilities.
"""

from typing import Any, Dict, List, Optional

from repomesh.agents.backend import BackendAgent
from repomesh.agents.base import BaseAgent
from repomesh.agents.frontend import FrontendAgent
from repomesh.core.events import EventBus
from repomesh.core.exceptions import AgentNotFoundError
from repomesh.core.models import AgentType
from repomesh.context.manager import SharedContextManager


class AgentRegistry:
    """Registry for managing agents."""

    def __init__(
        self,
        context_manager: SharedContextManager,
        event_bus: EventBus,
    ) -> None:
        """Initialize the agent registry.

        Args:
            context_manager: Shared context manager
            event_bus: Event bus for communication
        """
        self.context_manager = context_manager
        self.event_bus = event_bus
        self.agents: Dict[AgentType, BaseAgent] = {}
        self._register_default_agents()

    def _register_default_agents(self) -> None:
        """Register default agents."""
        # Register frontend agent
        frontend_agent = FrontendAgent(
            context_manager=self.context_manager,
            event_bus=self.event_bus,
        )
        self.register_agent(AgentType.FRONTEND, frontend_agent)

        # Register backend agent
        backend_agent = BackendAgent(
            context_manager=self.context_manager,
            event_bus=self.event_bus,
        )
        self.register_agent(AgentType.BACKEND, backend_agent)

    def register_agent(self, agent_type: AgentType, agent: BaseAgent) -> None:
        """Register an agent.

        Args:
            agent_type: Type of agent
            agent: Agent instance
        """
        self.agents[agent_type] = agent

    def get_agent(self, agent_type: AgentType) -> BaseAgent:
        """Get an agent by type.

        Args:
            agent_type: Type of agent

        Returns:
            Agent instance

        Raises:
            AgentNotFoundError: If agent not found
        """
        if agent_type not in self.agents:
            raise AgentNotFoundError(agent_type.value)

        return self.agents[agent_type]

    def list_agents(self) -> List[AgentType]:
        """List all registered agent types.

        Returns:
            List of agent types
        """
        return list(self.agents.keys())

    def get_capabilities(self, agent_type: AgentType) -> Dict[str, Any]:
        """Get capabilities for an agent.

        Args:
            agent_type: Type of agent

        Returns:
            Agent capabilities

        Raises:
            AgentNotFoundError: If agent not found
        """
        agent = self.get_agent(agent_type)
        return agent.get_capabilities()

    def get_all_capabilities(self) -> Dict[AgentType, Dict[str, Any]]:
        """Get capabilities for all agents.

        Returns:
            Dictionary mapping agent types to capabilities
        """
        return {
            agent_type: agent.get_capabilities()
            for agent_type, agent in self.agents.items()
        }

    def find_agents_for_repo_type(self, repo_type: str) -> List[AgentType]:
        """Find agents that support a repository type.

        Args:
            repo_type: Repository type

        Returns:
            List of agent types that support the repo type
        """
        matching_agents = []

        for agent_type, agent in self.agents.items():
            capabilities = agent.get_capabilities()
            supported_types = capabilities.get("supported_repo_types", [])
            if repo_type.lower() in [t.lower() for t in supported_types]:
                matching_agents.append(agent_type)

        return matching_agents

    def find_agents_for_task(self, task_type: str) -> List[AgentType]:
        """Find agents that support a task type.

        Args:
            task_type: Task type

        Returns:
            List of agent types that support the task type
        """
        matching_agents = []

        for agent_type, agent in self.agents.items():
            capabilities = agent.get_capabilities()
            supported_tasks = capabilities.get("supported_tasks", [])
            if task_type.lower() in [t.lower() for t in supported_tasks]:
                matching_agents.append(agent_type)

        return matching_agents

    def unregister_agent(self, agent_type: AgentType) -> None:
        """Unregister an agent.

        Args:
            agent_type: Type of agent to unregister
        """
        if agent_type in self.agents:
            del self.agents[agent_type]

# Made with Bob
