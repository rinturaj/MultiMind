"""
FastAPI application for RepoMesh AI.

This module provides the main FastAPI application with all endpoints
for repository management, orchestration, and context access.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from repomesh.agents.registry import AgentRegistry
from repomesh.context.manager import SharedContextManager
from repomesh.context.store import InMemoryStore
from repomesh.core.events import EventBus
from repomesh.orchestrator.workflow import OrchestrationWorkflow
from repomesh.repos.manager import RepoManager


# Global instances
repo_manager: RepoManager | None = None
context_manager: SharedContextManager | None = None
event_bus: EventBus | None = None
agent_registry: AgentRegistry | None = None
orchestrator: OrchestrationWorkflow | None = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan manager.

    Args:
        app: FastAPI application

    Yields:
        None
    """
    # Startup
    global repo_manager, context_manager, event_bus, agent_registry, orchestrator

    # Initialize services
    repo_manager = RepoManager()
    event_bus = EventBus()
    context_store = InMemoryStore()
    context_manager = SharedContextManager(context_store, event_bus)
    agent_registry = AgentRegistry(context_manager, event_bus)
    orchestrator = OrchestrationWorkflow(
        repo_manager=repo_manager,
        agent_registry=agent_registry,
        context_manager=context_manager,
        event_bus=event_bus,
    )

    yield

    # Shutdown
    # Clean up resources if needed
    pass


# Create FastAPI app
app = FastAPI(
    title="RepoMesh AI",
    description="Multi-agent AI system for coordinated repository analysis",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on environment
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependency injection functions
def get_repo_manager() -> RepoManager:
    """Get repository manager instance."""
    if repo_manager is None:
        raise RuntimeError("RepoManager not initialized")
    return repo_manager


def get_context_manager() -> SharedContextManager:
    """Get context manager instance."""
    if context_manager is None:
        raise RuntimeError("SharedContextManager not initialized")
    return context_manager


def get_event_bus() -> EventBus:
    """Get event bus instance."""
    if event_bus is None:
        raise RuntimeError("EventBus not initialized")
    return event_bus


def get_agent_registry() -> AgentRegistry:
    """Get agent registry instance."""
    if agent_registry is None:
        raise RuntimeError("AgentRegistry not initialized")
    return agent_registry


def get_orchestrator() -> OrchestrationWorkflow:
    """Get orchestrator instance."""
    if orchestrator is None:
        raise RuntimeError("OrchestrationWorkflow not initialized")
    return orchestrator


# Import routers
from repomesh.api.routes import context, health, orchestration, repositories

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(repositories.router, prefix="/api/v1", tags=["Repositories"])
app.include_router(orchestration.router, prefix="/api/v1", tags=["Orchestration"])
app.include_router(context.router, prefix="/api/v1", tags=["Context"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
