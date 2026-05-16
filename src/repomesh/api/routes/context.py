"""
Context management endpoints.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from repomesh.api.main import get_context_manager
from repomesh.context.manager import SharedContextManager

router = APIRouter()


class ContextSearchRequest(BaseModel):
    """Request model for context search."""

    query: str = Field(..., description="Search query")
    repo_id: Optional[str] = Field(None, description="Repository ID filter")
    top_k: int = Field(10, description="Number of results to return", ge=1, le=100)


class ContextEntry(BaseModel):
    """Response model for context entry."""

    id: str
    key: str
    content: str
    metadata: Dict[str, Any]
    repo_id: Optional[str]
    agent_type: Optional[str]
    created_at: str


class ContextSearchResponse(BaseModel):
    """Response model for context search."""

    query: str
    results: List[ContextEntry]
    count: int


@router.post("/context/search", response_model=ContextSearchResponse)
async def search_context(
    request: ContextSearchRequest,
    context_manager: SharedContextManager = Depends(get_context_manager),
) -> ContextSearchResponse:
    """Search for context entries.

    Args:
        request: Search request
        context_manager: Context manager

    Returns:
        Search results
    """
    try:
        # Convert repo_id if provided
        repo_id = UUID(request.repo_id) if request.repo_id else None

        # Search context
        results = await context_manager.get_relevant_context(
            query=request.query,
            repo_id=repo_id,
            top_k=request.top_k,
        )

        # Convert to response model
        entries = [
            ContextEntry(
                id=str(entry.id),
                key=entry.key,
                content=entry.content,
                metadata=entry.metadata,
                repo_id=str(entry.repo_id) if entry.repo_id else None,
                agent_type=entry.agent_type.value if entry.agent_type else None,
                created_at=entry.created_at.isoformat(),
            )
            for entry in results
        ]

        return ContextSearchResponse(
            query=request.query,
            results=entries,
            count=len(entries),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/keys", response_model=List[str])
async def list_context_keys(
    repo_id: Optional[str] = None,
    context_manager: SharedContextManager = Depends(get_context_manager),
) -> List[str]:
    """List all context keys.

    Args:
        repo_id: Optional repository ID filter
        context_manager: Context manager

    Returns:
        List of context keys
    """
    try:
        # Convert repo_id if provided
        repo_uuid = UUID(repo_id) if repo_id else None

        # Get keys
        keys = await context_manager.list_all_keys(repo_id=repo_uuid)

        return keys

    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid UUID: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/{key}", response_model=ContextEntry)
async def get_context_by_key(
    key: str,
    context_manager: SharedContextManager = Depends(get_context_manager),
) -> ContextEntry:
    """Get context by key.

    Args:
        key: Context key
        context_manager: Context manager

    Returns:
        Context entry
    """
    try:
        entry = await context_manager.get_context_by_key(key)

        if not entry:
            raise HTTPException(status_code=404, detail="Context not found")

        return ContextEntry(
            id=str(entry.id),
            key=entry.key,
            content=entry.content,
            metadata=entry.metadata,
            repo_id=str(entry.repo_id) if entry.repo_id else None,
            agent_type=entry.agent_type.value if entry.agent_type else None,
            created_at=entry.created_at.isoformat(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/context/{key}")
async def delete_context(
    key: str,
    context_manager: SharedContextManager = Depends(get_context_manager),
) -> dict:
    """Delete a context entry.

    Args:
        key: Context key
        context_manager: Context manager

    Returns:
        Success message
    """
    try:
        deleted = await context_manager.delete_context(key)

        if not deleted:
            raise HTTPException(status_code=404, detail="Context not found")

        return {"message": "Context deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
