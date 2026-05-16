"""
Orchestration endpoints.
"""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from repomesh.api.main import get_orchestrator
from repomesh.orchestrator.workflow import OrchestrationWorkflow

router = APIRouter()


class OrchestrationRequest(BaseModel):
    """Request model for starting orchestration."""

    repo_ids: List[str] = Field(..., description="List of repository IDs to analyze")


class OrchestrationResponse(BaseModel):
    """Response model for orchestration results."""

    repo_ids: List[str]
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    execution_time_seconds: float
    results: Dict[str, Any]


@router.post("/orchestrate", response_model=OrchestrationResponse)
async def start_orchestration(
    request: OrchestrationRequest,
    orchestrator: OrchestrationWorkflow = Depends(get_orchestrator),
) -> OrchestrationResponse:
    """Start orchestration workflow for repositories.

    Args:
        request: Orchestration request
        orchestrator: Orchestration workflow

    Returns:
        Orchestration results
    """
    try:
        # Convert string IDs to UUIDs
        repo_ids = [UUID(repo_id) for repo_id in request.repo_ids]

        # Run orchestration
        result = await orchestrator.run(repo_ids)

        # Extract results
        completed_tasks = result.get("completed_tasks", [])
        failed_tasks = result.get("failed_tasks", [])
        agent_results = result.get("agent_results", {})

        return OrchestrationResponse(
            repo_ids=request.repo_ids,
            total_tasks=len(result.get("tasks", [])),
            completed_tasks=len(completed_tasks),
            failed_tasks=len(failed_tasks),
            execution_time_seconds=result.get("execution_time_seconds", 0.0),
            results=agent_results,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
