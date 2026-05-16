"""
Example script for running orchestration workflows.

This script demonstrates how to run multi-agent orchestration
to analyze registered repositories.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from repomesh.agents.registry import AgentRegistry
from repomesh.context.manager import SharedContextManager
from repomesh.context.store import InMemoryStore
from repomesh.core.events import EventBus
from repomesh.orchestrator.workflow import OrchestrationWorkflow
from repomesh.repos.manager import RepoManager
from repomesh.utils.logging import get_logger, setup_logging

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)


async def main() -> None:
    """Main function to demonstrate orchestration."""
    
    logger.info("🚀 RepoMesh AI - Orchestration Example")
    logger.info("=" * 60)
    
    # Initialize components
    logger.info("Initializing components...")
    repo_manager = RepoManager(base_path="./repos")
    event_bus = EventBus()
    context_store = InMemoryStore()
    context_manager = SharedContextManager(context_store, event_bus)
    agent_registry = AgentRegistry(context_manager, event_bus)
    
    orchestrator = OrchestrationWorkflow(
        repo_manager=repo_manager,
        agent_registry=agent_registry,
        context_manager=context_manager,
        event_bus=event_bus,
        max_steps=50,
    )
    logger.info("✓ Components initialized")
    
    # List available repositories
    repos = repo_manager.list_repos()
    
    if not repos:
        logger.warning("⚠ No repositories registered!")
        logger.info("Please run register_repos.py first to register repositories.")
        return
    
    logger.info(f"\n📋 Found {len(repos)} registered repositories:")
    for i, repo in enumerate(repos, 1):
        logger.info(f"{i}. {repo.name} ({repo.repo_type.value}) - ID: {repo.id}")
    
    # Select repositories to analyze
    logger.info("\n🎯 Select repositories to analyze:")
    selection = input("Enter repository numbers (comma-separated, or 'all'): ").strip()
    
    if selection.lower() == "all":
        selected_repos = repos
    else:
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(",")]
            selected_repos = [repos[i] for i in indices if 0 <= i < len(repos)]
        except (ValueError, IndexError):
            logger.error("Invalid selection!")
            return
    
    if not selected_repos:
        logger.error("No repositories selected!")
        return
    
    repo_ids = [repo.id for repo in selected_repos]
    logger.info(f"\n🔄 Starting orchestration for {len(selected_repos)} repositories...")
    logger.info("-" * 60)
    
    # Run orchestration
    try:
        result = await orchestrator.run(repo_ids)
        
        # Display results
        logger.info("\n✓ Orchestration completed!")
        logger.info("=" * 60)
        logger.info(f"Execution Time: {result.get('execution_time_seconds', 0):.2f}s")
        logger.info(f"Total Tasks: {len(result.get('tasks', []))}")
        logger.info(f"Completed: {len(result.get('completed_tasks', []))}")
        logger.info(f"Failed: {len(result.get('failed_tasks', []))}")
        
        # Display agent results
        agent_results = result.get("agent_results", {})
        if agent_results:
            logger.info("\n📊 Agent Results:")
            logger.info("-" * 60)
            
            for task_id, task_result in agent_results.items():
                logger.info(f"\nTask: {task_id}")
                
                # Frontend results
                if "components" in task_result:
                    components = task_result["components"]
                    logger.info(f"  Frontend Analysis:")
                    logger.info(f"    - Components: {len(components)}")
                    logger.info(f"    - UI Patterns: {len(task_result.get('ui_patterns', []))}")
                    logger.info(f"    - API Integrations: {len(task_result.get('api_integrations', []))}")
                
                # Backend results
                if "endpoints" in task_result:
                    endpoints = task_result["endpoints"]
                    logger.info(f"  Backend Analysis:")
                    logger.info(f"    - API Endpoints: {len(endpoints)}")
                    logger.info(f"    - Schemas: {len(task_result.get('schemas', []))}")
                    logger.info(f"    - Dependencies: {len(task_result.get('dependencies', []))}")
                
                # Summary
                if "summary" in task_result:
                    logger.info(f"  Summary: {task_result['summary']}")
        
        # Display context updates
        context_updates = result.get("context_updates", [])
        if context_updates:
            logger.info(f"\n💾 Context Updates: {len(context_updates)}")
            logger.info("Context has been stored and is available for querying.")
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Example completed successfully!")
        
    except Exception as e:
        logger.error(f"✗ Orchestration failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
