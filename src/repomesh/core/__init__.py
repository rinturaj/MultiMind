"""
Core module for RepoMesh AI.

This module contains core data models, types, and exceptions used throughout the system.
"""

from repomesh.core.events import EventBus
from repomesh.core.exceptions import (
    AgentExecutionError,
    AgentNotFoundError,
    ConfigurationError,
    ContextStoreError,
    EventBusError,
    LLMError,
    OrchestrationError,
    RepoAlreadyExistsError,
    RepoCloneError,
    RepoMeshError,
    RepoNotFoundError,
    TaskExecutionError,
    TaskNotFoundError,
    ValidationError,
)
from repomesh.core.models import (
    AgentType,
    ContextEntry,
    Event,
    EventType,
    FileInfo,
    RepoMetadata,
    RepoType,
    Task,
    TaskStatus,
)
from repomesh.core.types import (
    AgentCapabilities,
    ContextSearchResult,
    OrchestrationState,
    RepoSummary,
)

__all__ = [
    # Events
    "EventBus",
    # Models
    "AgentType",
    "ContextEntry",
    "Event",
    "EventType",
    "FileInfo",
    "RepoMetadata",
    "RepoType",
    "Task",
    "TaskStatus",
    # Types
    "AgentCapabilities",
    "ContextSearchResult",
    "OrchestrationState",
    "RepoSummary",
    # Exceptions
    "AgentExecutionError",
    "AgentNotFoundError",
    "ConfigurationError",
    "ContextStoreError",
    "EventBusError",
    "LLMError",
    "OrchestrationError",
    "RepoAlreadyExistsError",
    "RepoCloneError",
    "RepoMeshError",
    "RepoNotFoundError",
    "TaskExecutionError",
    "TaskNotFoundError",
    "ValidationError",
]

# Made with Bob
