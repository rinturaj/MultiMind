"""
Execution tracing for RepoMesh AI.

This module provides execution tracing capabilities for monitoring
and debugging orchestration workflows.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TraceEvent(BaseModel):
    """A single trace event."""

    id: UUID = Field(default_factory=uuid4, description="Event ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    event_type: str = Field(..., description="Type of event")
    component: str = Field(..., description="Component that generated the event")
    message: str = Field(..., description="Event message")
    data: Dict[str, Any] = Field(default_factory=dict, description="Additional event data")
    level: str = Field(default="INFO", description="Event level (DEBUG, INFO, WARNING, ERROR)")


class ExecutionTrace(BaseModel):
    """Complete execution trace.
    
    Attributes:
        id: Unique trace identifier
        started_at: Timestamp when trace started
        completed_at: Timestamp when trace completed (None if still running)
        duration_seconds: Total execution duration in seconds
        status: Current trace status (running, completed, failed, etc.)
        events: List of trace events in chronological order
        metadata: Additional trace metadata dictionary
            Expected keys (all optional):
            - workflow_id: ID of the workflow being traced
            - repo_ids: List of repository IDs involved
            - agent_types: List of agent types used
            - user_id: ID of user who initiated the trace
            - tags: List of tags for categorization
            - Any other custom key-value pairs
    """

    id: UUID = Field(default_factory=uuid4, description="Trace ID")
    started_at: datetime = Field(default_factory=datetime.utcnow, description="Start time")
    completed_at: Optional[datetime] = Field(None, description="Completion time")
    duration_seconds: Optional[float] = Field(None, description="Execution duration")
    status: str = Field(default="running", description="Trace status")
    events: List[TraceEvent] = Field(default_factory=list, description="Trace events")
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Trace metadata (workflow_id, repo_ids, agent_types, user_id, tags, etc.)"
    )


class ExecutionTracer:
    """Manages execution tracing."""

    def __init__(self, output_dir: str = "./traces", enabled: bool = True) -> None:
        """Initialize the execution tracer.

        Args:
            output_dir: Directory for trace output
            enabled: Whether tracing is enabled
        """
        self.output_dir = Path(output_dir)
        self.enabled = enabled
        self.current_trace: Optional[ExecutionTrace] = None

        if self.enabled:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def start_trace(self, metadata: Optional[Dict[str, Any]] = None) -> UUID:
        """Start a new execution trace.

        Args:
            metadata: Optional trace metadata dictionary. If provided, must be a dict.
                Common keys include:
                - workflow_id: ID of the workflow being traced
                - repo_ids: List of repository IDs involved
                - agent_types: List of agent types used
                - user_id: ID of user who initiated the trace
                - tags: List of tags for categorization
                Any custom key-value pairs are also supported.

        Returns:
            Trace ID (UUID)
            
        Raises:
            TypeError: If metadata is not None and not a dictionary
            
        Example:
            >>> tracer = ExecutionTracer()
            >>> trace_id = tracer.start_trace({
            ...     "workflow_id": "wf-123",
            ...     "repo_ids": ["repo-1", "repo-2"],
            ...     "agent_types": ["frontend", "backend"],
            ...     "tags": ["production", "critical"]
            ... })
        """
        if not self.enabled:
            return uuid4()

        # Validate metadata parameter
        if metadata is not None and not isinstance(metadata, dict):
            raise TypeError(
                f"metadata must be a dictionary, got {type(metadata).__name__}"
            )

        # Initialize with validated metadata (empty dict if None)
        validated_metadata = metadata if metadata is not None else {}
        
        self.current_trace = ExecutionTrace(
            metadata=validated_metadata,
            completed_at=None,
            duration_seconds=None
        )
        return self.current_trace.id

    def add_event(
        self,
        event_type: str,
        component: str,
        message: str,
        data: Optional[Dict[str, Any]] = None,
        level: str = "INFO",
    ) -> None:
        """Add an event to the current trace.

        Args:
            event_type: Type of event
            component: Component name
            message: Event message
            data: Optional event data
            level: Event level
        """
        if not self.enabled or not self.current_trace:
            return

        event = TraceEvent(
            event_type=event_type,
            component=component,
            message=message,
            data=data or {},
            level=level,
        )
        self.current_trace.events.append(event)

    def complete_trace(self, status: str = "completed") -> Optional[UUID]:
        """Complete the current trace.

        Args:
            status: Final trace status

        Returns:
            Trace ID if trace exists
        """
        if not self.enabled or not self.current_trace:
            return None

        self.current_trace.completed_at = datetime.utcnow()
        self.current_trace.status = status

        # Calculate duration
        if self.current_trace.started_at and self.current_trace.completed_at:
            duration = (
                self.current_trace.completed_at - self.current_trace.started_at
            ).total_seconds()
            self.current_trace.duration_seconds = duration

        # Save trace
        trace_id = self.current_trace.id
        self._save_trace(self.current_trace)

        # Clear current trace
        self.current_trace = None

        return trace_id

    def _save_trace(self, trace: ExecutionTrace) -> None:
        """Save trace to file.

        Args:
            trace: Trace to save
        """
        if not self.enabled:
            return

        # Create filename with timestamp
        timestamp = trace.started_at.strftime("%Y%m%d_%H%M%S")
        filename = f"trace_{timestamp}_{trace.id}.json"
        filepath = self.output_dir / filename

        # Save as JSON
        with open(filepath, "w") as f:
            json.dump(trace.model_dump(mode="json"), f, indent=2, default=str)

    def get_current_trace(self) -> Optional[ExecutionTrace]:
        """Get the current trace.

        Returns:
            Current trace or None
        """
        return self.current_trace

    def load_trace(self, trace_id: UUID) -> Optional[ExecutionTrace]:
        """Load a trace from file.

        Args:
            trace_id: Trace ID to load

        Returns:
            Loaded trace or None
        """
        if not self.enabled:
            return None

        # Find trace file
        for filepath in self.output_dir.glob(f"trace_*_{trace_id}.json"):
            with open(filepath, "r") as f:
                data = json.load(f)
                return ExecutionTrace(**data)

        return None

    def list_traces(self, limit: int = 100) -> List[ExecutionTrace]:
        """List recent traces.

        Args:
            limit: Maximum number of traces to return

        Returns:
            List of traces
        """
        if not self.enabled:
            return []

        traces = []
        for filepath in sorted(self.output_dir.glob("trace_*.json"), reverse=True)[:limit]:
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    traces.append(ExecutionTrace(**data))
            except Exception:
                continue

        return traces


# Global tracer instance
_tracer: ExecutionTracer | None = None


def get_tracer() -> ExecutionTracer:
    """Get global tracer instance.

    Returns:
        ExecutionTracer instance
    """
    global _tracer
    if _tracer is None:
        from repomesh.utils.config import get_settings

        settings = get_settings()
        _tracer = ExecutionTracer(
            output_dir=settings.trace_output_dir,
            enabled=settings.enable_tracing,
        )
    return _tracer

# Made with Bob
