"""
Agent module for RepoMesh AI.

This module provides specialized agents for analyzing different types of repositories,
including frontend, backend, and other specialized agents.
"""

from repomesh.agents.backend import BackendAgent
from repomesh.agents.base import BaseAgent
from repomesh.agents.frontend import FrontendAgent
from repomesh.agents.registry import AgentRegistry

__all__ = [
    "BaseAgent",
    "FrontendAgent",
    "BackendAgent",
    "AgentRegistry",
]

# Made with Bob
