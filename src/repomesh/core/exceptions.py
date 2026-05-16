"""
Custom exceptions for RepoMesh AI.

This module defines all custom exceptions used throughout the system
for better error handling and debugging.
"""


class RepoMeshError(Exception):
    """Base exception for all RepoMesh errors."""

    pass


class RepoNotFoundError(RepoMeshError):
    """Raised when a repository is not found."""

    def __init__(self, repo_id: str) -> None:
        self.repo_id = repo_id
        super().__init__(f"Repository not found: {repo_id}")


class RepoAlreadyExistsError(RepoMeshError):
    """Raised when attempting to register a repository that already exists."""

    def __init__(self, repo_path: str) -> None:
        self.repo_path = repo_path
        super().__init__(f"Repository already exists: {repo_path}")


class RepoCloneError(RepoMeshError):
    """Raised when repository cloning fails."""

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to clone repository {url}: {reason}")


class TaskNotFoundError(RepoMeshError):
    """Raised when a task is not found."""

    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        super().__init__(f"Task not found: {task_id}")


class TaskExecutionError(RepoMeshError):
    """Raised when task execution fails."""

    def __init__(self, task_id: str, reason: str) -> None:
        self.task_id = task_id
        self.reason = reason
        super().__init__(f"Task {task_id} execution failed: {reason}")


class AgentNotFoundError(RepoMeshError):
    """Raised when an agent is not found."""

    def __init__(self, agent_type: str) -> None:
        self.agent_type = agent_type
        super().__init__(f"Agent not found: {agent_type}")


class AgentExecutionError(RepoMeshError):
    """Raised when agent execution fails."""

    def __init__(self, agent_type: str, reason: str) -> None:
        self.agent_type = agent_type
        self.reason = reason
        super().__init__(f"Agent {agent_type} execution failed: {reason}")


class ContextStoreError(RepoMeshError):
    """Raised when context store operations fail."""

    def __init__(self, operation: str, reason: str) -> None:
        self.operation = operation
        self.reason = reason
        super().__init__(f"Context store {operation} failed: {reason}")


class OrchestrationError(RepoMeshError):
    """Raised when orchestration fails."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(f"Orchestration failed: {reason}")


class ConfigurationError(RepoMeshError):
    """Raised when configuration is invalid."""

    def __init__(self, setting: str, reason: str) -> None:
        self.setting = setting
        self.reason = reason
        super().__init__(f"Invalid configuration for {setting}: {reason}")


class ValidationError(RepoMeshError):
    """Raised when data validation fails."""

    def __init__(self, field: str, reason: str) -> None:
        self.field = field
        self.reason = reason
        super().__init__(f"Validation failed for {field}: {reason}")


class EventBusError(RepoMeshError):
    """Raised when event bus operations fail."""

    def __init__(self, operation: str, reason: str) -> None:
        self.operation = operation
        self.reason = reason
        super().__init__(f"Event bus {operation} failed: {reason}")


class LLMError(RepoMeshError):
    """Raised when LLM operations fail."""

    def __init__(self, operation: str, reason: str) -> None:
        self.operation = operation
        self.reason = reason
        super().__init__(f"LLM {operation} failed: {reason}")

# Made with Bob
