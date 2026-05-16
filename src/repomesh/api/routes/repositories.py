"""
Repository management endpoints.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from repomesh.api.main import get_repo_manager
from repomesh.core.models import RepoMetadata, RepoType
from repomesh.repos.manager import RepoManager

router = APIRouter()


class RegisterRepoRequest(BaseModel):
    """Request model for registering a repository."""

    url: Optional[str] = Field(None, description="Git repository URL")
    path: Optional[str] = Field(None, description="Local repository path")
    name: Optional[str] = Field(None, description="Repository name")


class RepoResponse(BaseModel):
    """Response model for repository information."""

    id: str
    name: str
    path: str
    url: Optional[str]
    repo_type: str
    tech_stack: List[str]
    file_count: int
    code_file_count: int
    total_lines: int
    summary: Optional[str]


@router.post("/repos/register", response_model=RepoResponse)
async def register_repository(
    request: RegisterRepoRequest,
    repo_manager: RepoManager = Depends(get_repo_manager),
) -> RepoResponse:
    """Register a new repository.

    Args:
        request: Registration request
        repo_manager: Repository manager

    Returns:
        Repository information
    """
    try:
        if request.url:
            # Clone remote repository
            metadata = repo_manager.clone_repo(
                url=request.url,
                name=request.name,
            )
        elif request.path:
            # Load local repository
            metadata = repo_manager.load_local_repo(
                path=request.path,
                url=request.url,
            )
        else:
            raise HTTPException(
                status_code=400,
                detail="Either 'url' or 'path' must be provided",
            )

        return RepoResponse(
            id=str(metadata.id),
            name=metadata.name,
            path=metadata.path,
            url=metadata.url,
            repo_type=metadata.repo_type.value,
            tech_stack=metadata.tech_stack,
            file_count=metadata.file_count,
            code_file_count=metadata.code_file_count,
            total_lines=metadata.total_lines,
            summary=metadata.summary,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/repos", response_model=List[RepoResponse])
async def list_repositories(
    repo_manager: RepoManager = Depends(get_repo_manager),
) -> List[RepoResponse]:
    """List all registered repositories.

    Args:
        repo_manager: Repository manager

    Returns:
        List of repositories
    """
    repos = repo_manager.list_repos()
    return [
        RepoResponse(
            id=str(repo.id),
            name=repo.name,
            path=repo.path,
            url=repo.url,
            repo_type=repo.repo_type.value,
            tech_stack=repo.tech_stack,
            file_count=repo.file_count,
            code_file_count=repo.code_file_count,
            total_lines=repo.total_lines,
            summary=repo.summary,
        )
        for repo in repos
    ]


@router.get("/repos/{repo_id}", response_model=RepoResponse)
async def get_repository(
    repo_id: UUID,
    repo_manager: RepoManager = Depends(get_repo_manager),
) -> RepoResponse:
    """Get repository by ID.

    Args:
        repo_id: Repository ID
        repo_manager: Repository manager

    Returns:
        Repository information
    """
    try:
        metadata = repo_manager.get_repo_metadata(repo_id)
        return RepoResponse(
            id=str(metadata.id),
            name=metadata.name,
            path=metadata.path,
            url=metadata.url,
            repo_type=metadata.repo_type.value,
            tech_stack=metadata.tech_stack,
            file_count=metadata.file_count,
            code_file_count=metadata.code_file_count,
            total_lines=metadata.total_lines,
            summary=metadata.summary,
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/repos/{repo_id}")
async def delete_repository(
    repo_id: UUID,
    delete_files: bool = False,
    repo_manager: RepoManager = Depends(get_repo_manager),
) -> dict:
    """Delete a repository.

    Args:
        repo_id: Repository ID
        delete_files: Whether to delete repository files
        repo_manager: Repository manager

    Returns:
        Success message
    """
    try:
        repo_manager.remove_repo(repo_id, delete_files=delete_files)
        return {"message": "Repository deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

# Made with Bob
