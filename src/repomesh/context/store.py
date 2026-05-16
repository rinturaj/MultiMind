"""
Context store interfaces and implementations.

This module provides abstract and concrete implementations of context stores
for managing shared context between agents.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from uuid import UUID

from repomesh.core.models import AgentType, ContextEntry


class ContextStore(ABC):
    """Abstract interface for context storage."""

    @abstractmethod
    async def store(
        self,
        key: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
    ) -> ContextEntry:
        """Store a context entry.

        Args:
            key: Context key
            content: Context content
            metadata: Optional metadata
            repo_id: Optional repository ID
            agent_type: Optional agent type

        Returns:
            Created context entry
        """
        pass

    @abstractmethod
    async def retrieve(self, key: str) -> Optional[ContextEntry]:
        """Retrieve a context entry by key.

        Args:
            key: Context key

        Returns:
            Context entry or None if not found
        """
        pass

    @abstractmethod
    async def search(
        self,
        query: str,
        top_k: int = 10,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
    ) -> List[ContextEntry]:
        """Search for context entries.

        Args:
            query: Search query
            top_k: Number of results to return
            repo_id: Optional repository ID filter
            agent_type: Optional agent type filter

        Returns:
            List of matching context entries
        """
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete a context entry.

        Args:
            key: Context key

        Returns:
            True if deleted, False if not found
        """
        pass

    @abstractmethod
    async def list_keys(
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
        pass


class InMemoryStore(ContextStore):
    """In-memory implementation of context store."""

    def __init__(self) -> None:
        """Initialize the in-memory store."""
        self.entries: Dict[str, ContextEntry] = {}

    async def store(
        self,
        key: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
    ) -> ContextEntry:
        """Store a context entry."""
        entry = ContextEntry(
            key=key,
            content=content,
            metadata=metadata or {},
            repo_id=repo_id,
            agent_type=agent_type,
        )
        self.entries[key] = entry
        return entry

    async def retrieve(self, key: str) -> Optional[ContextEntry]:
        """Retrieve a context entry by key."""
        return self.entries.get(key)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
    ) -> List[ContextEntry]:
        """Search for context entries using substring matching."""
        results: List[ContextEntry] = []
        query_lower = query.lower()

        for entry in self.entries.values():
            # Apply filters
            if repo_id and entry.repo_id != repo_id:
                continue
            if agent_type and entry.agent_type != agent_type:
                continue

            # Simple substring search
            if query_lower in entry.content.lower() or query_lower in entry.key.lower():
                results.append(entry)

        # Sort by relevance (simple: by key match first, then content match)
        results.sort(
            key=lambda e: (
                query_lower not in e.key.lower(),
                query_lower not in e.content.lower(),
            )
        )

        return results[:top_k]

    async def delete(self, key: str) -> bool:
        """Delete a context entry."""
        if key in self.entries:
            del self.entries[key]
            return True
        return False

    async def list_keys(
        self,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
    ) -> List[str]:
        """List all context keys."""
        keys: List[str] = []

        for key, entry in self.entries.items():
            # Apply filters
            if repo_id and entry.repo_id != repo_id:
                continue
            if agent_type and entry.agent_type != agent_type:
                continue

            keys.append(key)

        return sorted(keys)


class ChromaDBStore(ContextStore):
    """ChromaDB implementation of context store with vector embeddings."""

    def __init__(
        self,
        collection_name: str = "repomesh_context",
        persist_directory: str = "./data/chroma",
    ) -> None:
        """Initialize the ChromaDB store.

        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory to persist ChromaDB data
        """
        import chromadb
        from chromadb.config import Settings

        self.client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )
        self.collection = self.client.get_or_create_collection(name=collection_name)
        self.entries: Dict[str, ContextEntry] = {}

    async def store(
        self,
        key: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
    ) -> ContextEntry:
        """Store a context entry with vector embedding."""
        entry = ContextEntry(
            key=key,
            content=content,
            metadata=metadata or {},
            repo_id=repo_id,
            agent_type=agent_type,
        )

        # Prepare metadata for ChromaDB
        chroma_metadata = {
            "key": key,
            "repo_id": str(repo_id) if repo_id else "",
            "agent_type": agent_type.value if agent_type else "",
        }
        chroma_metadata.update(metadata or {})

        # Store in ChromaDB
        self.collection.add(
            documents=[content],
            metadatas=[chroma_metadata],
            ids=[key],
        )

        # Store entry for retrieval
        self.entries[key] = entry

        return entry

    async def retrieve(self, key: str) -> Optional[ContextEntry]:
        """Retrieve a context entry by key."""
        return self.entries.get(key)

    async def search(
        self,
        query: str,
        top_k: int = 10,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
    ) -> List[ContextEntry]:
        """Search for context entries using vector similarity."""
        # Build where clause for filtering
        where_clause: Dict[str, Any] = {}
        if repo_id:
            where_clause["repo_id"] = str(repo_id)
        if agent_type:
            where_clause["agent_type"] = agent_type.value

        # Query ChromaDB
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_clause if where_clause else None,
        )

        # Convert to ContextEntry objects
        entries: List[ContextEntry] = []
        if results["ids"] and results["ids"][0]:
            for key in results["ids"][0]:
                if key in self.entries:
                    entries.append(self.entries[key])

        return entries

    async def delete(self, key: str) -> bool:
        """Delete a context entry."""
        try:
            self.collection.delete(ids=[key])
            if key in self.entries:
                del self.entries[key]
            return True
        except Exception:
            return False

    async def list_keys(
        self,
        repo_id: Optional[UUID] = None,
        agent_type: Optional[AgentType] = None,
    ) -> List[str]:
        """List all context keys."""
        keys: List[str] = []

        for key, entry in self.entries.items():
            # Apply filters
            if repo_id and entry.repo_id != repo_id:
                continue
            if agent_type and entry.agent_type != agent_type:
                continue

            keys.append(key)

        return sorted(keys)

# Made with Bob
