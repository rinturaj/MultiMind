"""
RepoMesh AI - Multi-agent AI system for coordinated repository analysis.

This package provides a comprehensive framework for analyzing and coordinating
work across multiple repositories using specialized AI agents.
"""

__version__ = "0.1.0"
__author__ = "RepoMesh Team"
__email__ = "team@repomesh.ai"

from repomesh.core.models import (
    AgentType,
    Event,
    EventType,
    FileInfo,
    RepoMetadata,
    RepoType,
    Task,
    TaskStatus,
)

__all__ = [
    "AgentType",
    "Event",
    "EventType",
    "FileInfo",
    "RepoMetadata",
    "RepoType",
    "Task",
    "TaskStatus",
]

# Made with Bob
