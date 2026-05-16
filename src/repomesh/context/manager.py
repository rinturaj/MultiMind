"""
Shared context manager for coordinating agent communication.

This module provides the main interface for managing shared context
between agents, including storing, retrieving, and searching context.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from repomesh.core.models import AgentType, ContextEntry, Event, EventType
from repomesh.context.store import ContextStore


class SharedContextManager:
    """Manages shared context between agents."""

    def __init__(
        self,
        store: ContextStore,
        event_bus: Optional[Any] = None,
    ) -> None:
        """Initialize the shared context manager.

        Args:
            store: Context store implementation
            event_bus: Optional event bus for publishing updates
        """
        self.store = store
        self.event_bus = event_bus

    async def store_architecture_note(
        self,
        content: str,
        repo_id: UUID,
        agent_type: AgentType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContextEntry:
        """Store an architecture note.

        Args:
            content: Architecture note content
            repo_id: Repository ID
            agent_type: Agent that created the note
            metadata: Optional metadata

        Returns:
            Created context entry
        """
        key = f"architecture:{repo_id}:{agent_type.value}"
        entry = await self.store.store(
            key=key,
            content=content,
            metadata={"type": "architecture", **(metadata or {})},
            repo_id=repo_id,
            agent_type=agent_type,
        )

        await self._publish_context_update(entry, "architecture_note_stored")
        return entry

    async def store_api_contract(
        self,
        content: str,
        repo_id: UUID,
        agent_type: AgentType,
        endpoint: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContextEntry:
        """Store an API contract.

        Args:
            content: API contract content
            repo_id: Repository ID
            agent_type: Agent that created the contract
            endpoint: API endpoint
            metadata: Optional metadata

        Returns:
            Created context entry
        """
        key = f"api_contract:{repo_id}:{endpoint}"
        entry = await self.store.store(
            key=key,
            content=content,
            metadata={"type": "api_contract", "endpoint": endpoint, **(metadata or {})},
            repo_id=repo_id,
            agent_type=agent_type,
        )

        await self._publish_context_update(entry, "api_contract_stored")
        return entry

    async def store_schema_change(
        self,
        content: str,
        repo_id: UUID,
        agent_type: AgentType,
        schema_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContextEntry:
        """Store a schema change.

        Args:
            content: Schema change content
            repo_id: Repository ID
            agent_type: Agent that created the change
            schema_name: Schema name
            metadata: Optional metadata

        Returns:
            Created context entry
        """
        key = f"schema_change:{repo_id}:{schema_name}"
        entry = await self.store.store(
            key=key,
            content=content,
            metadata={"type": "schema_change", "schema_name": schema_name, **(metadata or {})},
            repo_id=repo_id,
            agent_type=agent_type,
        )

        await self._publish_context_update(entry, "schema_change_stored")
        return entry

    async def store_component_info(
        self,
        content: str,
        repo_id: UUID,
        agent_type: AgentType,
        component_name: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContextEntry:
        """Store component information.

        Args:
            content: Component information content
            repo_id: Repository ID
            agent_type: Agent that created the info
            component_name: Component name
            metadata: Optional metadata

        Returns:
            Created context entry
        """
        key = f"component:{repo_id}:{component_name}"
        entry = await self.store.store(
            key=key,
            content=content,
            metadata={"type": "component", "component_name": component_name, **(metadata or {})},
            repo_id=repo_id,
            agent_type=agent_type,
        )

        await self._publish_context_update(entry, "component_info_stored")
        return entry

    async def store_dependency_info(
        self,
        content: str,
        repo_id: UUID,
        agent_type: AgentType,
        dependency_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ContextEntry:
        """Store dependency information.

        Args:
            content: Dependency information content
            repo_id: Repository ID
            agent_type: Agent that created the info
            dependency_type: Type of dependency
            metadata: Optional metadata

        Returns:
            Created context entry
        """
        key = f"dependency:{repo_id}:{dependency_type}"
        entry = await self.store.store(
            key=key,
            content=content,
            metadata={"type": "dependency", "dependency_type": dependency_type, **(metadata or {})},
            repo_id=repo_id,
            agent_type=agent_type,
        )

        await self._publish_context_update(entry, "dependency_info_stored")
        return entry

    async def get_relevant_context(
        self,
        query: str,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
        top_k: int = 10,
    ) -> List[ContextEntry]:
        """Get relevant context for a query.

        Args:
            query: Search query
            repo_id: Optional repository ID filter
            agent_type: Optional agent type filter
            top_k: Number of results to return

        Returns:
            List of relevant context entries
        """
        return await self.store.search(
            query=query,
            top_k=top_k,
            repo_id=repo_id,
            agent_type=agent_type,
        )

    async def get_context_by_key(self, key: str) -> Optional[ContextEntry]:
        """Get context by key.

        Args:
            key: Context key

        Returns:
            Context entry or None if not found
        """
        return await self.store.retrieve(key)

    async def get_architecture_notes(
        self,
        repo_id: UUID,
        agent_type: Optional[AgentType] = None,
    ) -> List[ContextEntry]:
        """Get architecture notes for a repository.

        Args:
            repo_id: Repository ID
            agent_type: Optional agent type filter

        Returns:
            List of architecture notes
        """
        return await self.store.search(
            query="architecture",
            repo_id=repo_id,
            agent_type=agent_type,
            top_k=100,
        )

    async def get_api_contracts(
        self,
        repo_id: UUID,
        agent_type: Optional[AgentType] = None,
    ) -> List[ContextEntry]:
        """Get API contracts for a repository.

        Args:
            repo_id: Repository ID
            agent_type: Optional agent type filter

        Returns:
            List of API contracts
        """
        return await self.store.search(
            query="api_contract",
            repo_id=repo_id,
            agent_type=agent_type,
            top_k=100,
        )

    async def delete_context(self, key: str) -> bool:
        """Delete a context entry.

        Args:
            key: Context key

        Returns:
            True if deleted, False if not found
        """
        deleted = await self.store.delete(key)
        if deleted and self.event_bus:
            await self.event_bus.publish(
                Event(
                    type=EventType.CONTEXT_UPDATED,
                    source="context_manager",
                    payload={"action": "deleted", "key": key},
                )
            )
        return deleted

    async def list_all_keys(
        self,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
    ) -> List[str]:
        """List all context keys.

        Args:
            repo_id: Optional repository ID filter
            agent_type: Optional agent type filter

        Returns:
            List of context keys
        """
        return await self.store.list_keys(repo_id=repo_id, agent_type=agent_type)

    async def _publish_context_update(self, entry: ContextEntry, action: str) -> None:
        """Publish a context update event.

        Args:
            entry: Context entry that was updated
            action: Action that was performed
        """
        if self.event_bus:
            await self.event_bus.publish(
                Event(
                    type=EventType.CONTEXT_UPDATED,
                    source="context_manager",
                    payload={
                        "action": action,
                        "key": entry.key,
                        "repo_id": str(entry.repo_id) if entry.repo_id else None,
                        "agent_type": entry.agent_type.value if entry.agent_type else None,
                    },
                    repo_id=entry.repo_id,
                )
            )

# Made with Bob
