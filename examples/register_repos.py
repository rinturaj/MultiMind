"""
Example script for registering repositories with RepoMesh AI.

This script demonstrates how to register both local and remote repositories.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from repomesh.core.events import EventBus
from repomesh.repos.manager import RepoManager
from repomesh.utils.logging import get_logger, setup_logging

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)


async def main() -> None:
    """Main function to demonstrate repository registration."""
    
    logger.info("🚀 RepoMesh AI - Repository Registration Example")
    logger.info("=" * 60)
    
    # Initialize repository manager
    repo_manager = RepoManager(base_path="./repos")
    logger.info("✓ Repository manager initialized")
    
    # Example 1: Register a local repository
    logger.info("\n📁 Example 1: Registering local repository...")
    try:
        local_repo_path = input("Enter path to local repository (or press Enter to skip): ").strip()
        
        if local_repo_path:
            metadata = repo_manager.load_local_repo(local_repo_path)
            logger.info(f"✓ Registered local repository: {metadata.name}")
            logger.info(f"  - ID: {metadata.id}")
            logger.info(f"  - Type: {metadata.repo_type.value}")
            logger.info(f"  - Files: {metadata.file_count} ({metadata.code_file_count} code files)")
            logger.info(f"  - Lines: {metadata.total_lines:,}")
            logger.info(f"  - Tech Stack: {', '.join(metadata.tech_stack[:5])}")
    except Exception as e:
        logger.error(f"✗ Failed to register local repository: {e}")
    
    # Example 2: Clone and register a remote repository
    logger.info("\n🌐 Example 2: Cloning remote repository...")
    try:
        remote_url = input("Enter Git repository URL (or press Enter to skip): ").strip()
        
        if remote_url:
            logger.info(f"Cloning {remote_url}...")
            metadata = repo_manager.clone_repo(remote_url)
            logger.info(f"✓ Cloned and registered repository: {metadata.name}")
            logger.info(f"  - ID: {metadata.id}")
            logger.info(f"  - Type: {metadata.repo_type.value}")
            logger.info(f"  - Files: {metadata.file_count} ({metadata.code_file_count} code files)")
            logger.info(f"  - Lines: {metadata.total_lines:,}")
            logger.info(f"  - Tech Stack: {', '.join(metadata.tech_stack[:5])}")
    except Exception as e:
        logger.error(f"✗ Failed to clone repository: {e}")
    
    # List all registered repositories
    logger.info("\n📋 All Registered Repositories:")
    logger.info("-" * 60)
    repos = repo_manager.list_repos()
    
    if repos:
        for i, repo in enumerate(repos, 1):
            logger.info(f"\n{i}. {repo.name}")
            logger.info(f"   ID: {repo.id}")
            logger.info(f"   Type: {repo.repo_type.value}")
            logger.info(f"   Path: {repo.path}")
            logger.info(f"   Files: {repo.file_count} ({repo.code_file_count} code)")
            logger.info(f"   Lines: {repo.total_lines:,}")
            if repo.tech_stack:
                logger.info(f"   Tech: {', '.join(repo.tech_stack[:3])}")
    else:
        logger.info("No repositories registered yet.")
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
