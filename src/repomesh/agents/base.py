"""
Base agent class for all specialized agents.

This module provides the abstract base class that all agents must inherit from,
defining the common interface and shared functionality.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from repomesh.core.events import EventBus
from repomesh.core.models import AgentType, Event, EventType, RepoMetadata, Task
from repomesh.context.manager import SharedContextManager


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(
        self,
        agent_type: AgentType,
        context_manager: SharedContextManager,
        event_bus: EventBus,
    ) -> None:
        """Initialize the base agent.

        Args:
            agent_type: Type of this agent
            context_manager: Shared context manager
            event_bus: Event bus for communication
        """
        self.agent_type = agent_type
        self.context_manager = context_manager
        self.event_bus = event_bus

    @abstractmethod
    async def process_task(
        self,
        task: Task,
        repo_metadata: RepoMetadata,
    ) -> Dict[str, Any]:
        """Process a task for a repository.

        Args:
            task: Task to process
            repo_metadata: Repository metadata

        Returns:
            Task result dictionary

        Raises:
            AgentExecutionError: If task processing fails
        """
        pass

    @abstractmethod
    def get_capabilities(self) -> Dict[str, Any]:
        """Get agent capabilities.

        Returns:
            Dictionary describing agent capabilities
        """
        pass

    async def publish_event(
        self,
        event_type: EventType,
        payload: Dict[str, Any],
        repo_id: Optional[UUID] = None,
        task_id: Optional[UUID] = None,
    ) -> None:
        """Publish an event to the event bus.

        Args:
            event_type: Type of event
            payload: Event payload
            repo_id: Optional repository ID
            task_id: Optional task ID
        """
        event = Event(
            type=event_type,
            source=f"{self.agent_type.value}_agent",
            payload=payload,
            repo_id=repo_id,
            task_id=task_id,
        )
        await self.event_bus.publish(event)

    async def get_context(
        self,
        query: str,
        repo_id: Optional[UUID] = None,
        top_k: int = 10,
    ) -> List[Any]:
        """Get relevant context from the context manager.

        Args:
            query: Search query
            repo_id: Optional repository ID filter
            top_k: Number of results to return

        Returns:
            List of relevant context entries
        """
        return await self.context_manager.get_relevant_context(
            query=query,
            repo_id=repo_id,
            agent_type=self.agent_type,
            top_k=top_k,
        )

    async def store_context(
        self,
        key: str,
        content: str,
        repo_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Store context in the shared context manager.

        Args:
            key: Context key
            content: Context content
            repo_id: Repository ID
            metadata: Optional metadata
        """
        await self.context_manager.store.store(
            key=key,
            content=content,
            metadata=metadata,
            repo_id=repo_id,
            agent_type=self.agent_type,
        )

    def _format_repo_summary(self, repo_metadata: RepoMetadata) -> str:
        """Format repository metadata into a summary string.

        Args:
            repo_metadata: Repository metadata

        Returns:
            Formatted summary string
        """
        return f"""
Repository: {repo_metadata.name}
Type: {repo_metadata.repo_type.value}
Tech Stack: {', '.join(repo_metadata.tech_stack) if repo_metadata.tech_stack else 'Unknown'}
Files: {repo_metadata.file_count} total, {repo_metadata.code_file_count} code files
Lines of Code: {repo_metadata.total_lines:,}
Path: {repo_metadata.path}
""".strip()

    def _get_code_files(self, repo_metadata: RepoMetadata, language: Optional[str] = None) -> List[Any]:
        """Get code files from repository metadata.

        Args:
            repo_metadata: Repository metadata
            language: Optional language filter

        Returns:
            List of code files
        """
        files = [f for f in repo_metadata.files if f.is_code]
        
        if language:
            files = [f for f in files if f.language and f.language.lower() == language.lower()]
        
        return files

    def _get_files_by_extension(self, repo_metadata: RepoMetadata, extensions: List[str]) -> List[Any]:
        """Get files by extension.

        Args:
            repo_metadata: Repository metadata
            extensions: List of extensions to filter by

        Returns:
            List of matching files
        """
        extensions_lower = [ext.lower() for ext in extensions]
        return [f for f in repo_metadata.files if f.extension.lower() in extensions_lower]

# Made with Bob
