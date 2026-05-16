"""
Core data models for RepoMesh AI.

This module defines all the core data structures used throughout the system,
including enums, Pydantic models, and TypedDicts for type safety.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class RepoType(str, Enum):
    """Type of repository."""

    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"
    MOBILE = "mobile"
    LIBRARY = "library"
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    UNKNOWN = "unknown"


class TaskStatus(str, Enum):
    """Status of a task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class EventType(str, Enum):
    """Type of event in the system."""

    REPO_REGISTERED = "repo_registered"
    REPO_SCANNED = "repo_scanned"
    TASK_CREATED = "task_created"
    TASK_STARTED = "task_started"
    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    CONTEXT_UPDATED = "context_updated"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    ORCHESTRATION_STARTED = "orchestration_started"
    ORCHESTRATION_COMPLETED = "orchestration_completed"
    ORCHESTRATION_FAILED = "orchestration_failed"


class AgentType(str, Enum):
    """Type of agent in the system."""

    FRONTEND = "frontend"
    BACKEND = "backend"
    DEVOPS = "devops"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    SECURITY = "security"


class FileInfo(BaseModel):
    """Information about a file in a repository."""

    path: str = Field(..., description="Relative path to the file")
    size: int = Field(..., description="File size in bytes", ge=0)
    extension: str = Field(..., description="File extension")
    is_code: bool = Field(default=False, description="Whether this is a code file")
    language: Optional[str] = Field(None, description="Programming language")
    lines: Optional[int] = Field(None, description="Number of lines", ge=0)

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate that path is not empty."""
        if not v or not v.strip():
            raise ValueError("Path cannot be empty")
        return v.strip()


class RepoMetadata(BaseModel):
    """Metadata about a repository."""

    id: UUID = Field(default_factory=uuid4, description="Unique repository ID")
    name: str = Field(..., description="Repository name")
    path: str = Field(..., description="Local path to repository")
    url: Optional[str] = Field(None, description="Remote repository URL")
    repo_type: RepoType = Field(default=RepoType.UNKNOWN, description="Type of repository")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies used")
    dependencies: Dict[str, str] = Field(
        default_factory=dict, description="Dependencies and versions"
    )
    file_count: int = Field(default=0, description="Total number of files", ge=0)
    code_file_count: int = Field(default=0, description="Number of code files", ge=0)
    total_lines: int = Field(default=0, description="Total lines of code", ge=0)
    files: List[FileInfo] = Field(default_factory=list, description="List of files")
    summary: Optional[str] = Field(None, description="Repository summary")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate that name is not empty."""
        if not v or not v.strip():
            raise ValueError("Repository name cannot be empty")
        return v.strip()

    @field_validator("path")
    @classmethod
    def validate_path(cls, v: str) -> str:
        """Validate that path is not empty."""
        if not v or not v.strip():
            raise ValueError("Repository path cannot be empty")
        return v.strip()

    def model_post_init(self, __context: Any) -> None:
        """Update timestamp after initialization."""
        self.updated_at = datetime.utcnow()


class Task(BaseModel):
    """A task to be executed by an agent."""

    id: UUID = Field(default_factory=uuid4, description="Unique task ID")
    repo_id: UUID = Field(..., description="Repository this task belongs to")
    agent_type: AgentType = Field(..., description="Type of agent to execute this task")
    description: str = Field(..., description="Task description")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current task status")
    priority: int = Field(default=5, description="Task priority (1-10)", ge=1, le=10)
    dependencies: List[UUID] = Field(
        default_factory=list, description="Task IDs this task depends on"
    )
    result: Optional[Dict[str, Any]] = Field(None, description="Task execution result")
    error: Optional[str] = Field(None, description="Error message if task failed")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate that description is not empty."""
        if not v or not v.strip():
            raise ValueError("Task description cannot be empty")
        return v.strip()

    def start(self) -> None:
        """Mark task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.utcnow()

    def complete(self, result: Optional[Dict[str, Any]] = None) -> None:
        """Mark task as completed."""
        self.status = TaskStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        if result:
            self.result = result

    def fail(self, error: str) -> None:
        """Mark task as failed."""
        self.status = TaskStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.error = error


class Event(BaseModel):
    """An event in the system."""

    id: UUID = Field(default_factory=uuid4, description="Unique event ID")
    type: EventType = Field(..., description="Type of event")
    source: str = Field(..., description="Source of the event (agent, orchestrator, etc.)")
    payload: Dict[str, Any] = Field(default_factory=dict, description="Event payload data")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    repo_id: Optional[UUID] = Field(None, description="Related repository ID")
    task_id: Optional[UUID] = Field(None, description="Related task ID")

    @field_validator("source")
    @classmethod
    def validate_source(cls, v: str) -> str:
        """Validate that source is not empty."""
        if not v or not v.strip():
            raise ValueError("Event source cannot be empty")
        return v.strip()


class ContextEntry(BaseModel):
    """An entry in the shared context store."""

    id: UUID = Field(default_factory=uuid4, description="Unique entry ID")
    key: str = Field(..., description="Context key")
    content: str = Field(..., description="Context content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    repo_id: Optional[UUID] = Field(None, description="Related repository ID")
    agent_type: Optional[AgentType] = Field(None, description="Agent that created this entry")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")

    @field_validator("key")
    @classmethod
    def validate_key(cls, v: str) -> str:
        """Validate that key is not empty."""
        if not v or not v.strip():
            raise ValueError("Context key cannot be empty")
        return v.strip()

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        """Validate that content is not empty."""
        if not v or not v.strip():
            raise ValueError("Context content cannot be empty")
        return v.strip()

    def model_post_init(self, __context: Any) -> None:
        """Update timestamp after initialization."""
        self.updated_at = datetime.utcnow()

# Made with Bob
