"""
Example script for inspecting shared context.

This script demonstrates how to query and inspect the shared context
that agents use for coordination.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from repomesh.context.manager import SharedContextManager
from repomesh.context.store import InMemoryStore
from repomesh.core.events import EventBus
from repomesh.utils.logging import get_logger, setup_logging

# Setup logging
setup_logging(level="INFO")
logger = get_logger(__name__)


async def main() -> None:
    """Main function to demonstrate context inspection."""
    
    logger.info("🚀 RepoMesh AI - Context Inspection Example")
    logger.info("=" * 60)
    
    # Initialize context manager
    event_bus = EventBus()
    context_store = InMemoryStore()
    context_manager = SharedContextManager(context_store, event_bus)
    logger.info("✓ Context manager initialized")
    
    # List all context keys
    logger.info("\n📋 Listing all context keys...")
    keys = await context_manager.list_all_keys()
    
    if not keys:
        logger.warning("⚠ No context entries found!")
        logger.info("Please run run_orchestration.py first to generate context.")
        return
    
    logger.info(f"Found {len(keys)} context entries:")
    for i, key in enumerate(keys, 1):
        logger.info(f"{i}. {key}")
    
    # Interactive context exploration
    while True:
        logger.info("\n" + "=" * 60)
        logger.info("Options:")
        logger.info("1. Search context")
        logger.info("2. View specific context entry")
        logger.info("3. List all keys")
        logger.info("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # Search context
            query = input("Enter search query: ").strip()
            if query:
                logger.info(f"\n🔍 Searching for: '{query}'")
                results = await context_manager.get_relevant_context(query, top_k=5)
                
                if results:
                    logger.info(f"Found {len(results)} results:")
                    for i, entry in enumerate(results, 1):
                        logger.info(f"\n{i}. Key: {entry.key}")
                        logger.info(f"   Agent: {entry.agent_type.value if entry.agent_type else 'N/A'}")
                        logger.info(f"   Created: {entry.created_at}")
                        logger.info(f"   Content Preview: {entry.content[:200]}...")
                        if entry.metadata:
                            logger.info(f"   Metadata: {entry.metadata}")
                else:
                    logger.info("No results found.")
        
        elif choice == "2":
            # View specific entry
            key = input("Enter context key: ").strip()
            if key:
                entry = await context_manager.get_context_by_key(key)
                
                if entry:
                    logger.info(f"\n📄 Context Entry: {entry.key}")
                    logger.info("-" * 60)
                    logger.info(f"ID: {entry.id}")
                    logger.info(f"Agent: {entry.agent_type.value if entry.agent_type else 'N/A'}")
                    logger.info(f"Repo ID: {entry.repo_id}")
                    logger.info(f"Created: {entry.created_at}")
                    logger.info(f"Updated: {entry.updated_at}")
                    logger.info(f"\nContent:")
                    logger.info(entry.content)
                    if entry.metadata:
                        logger.info(f"\nMetadata:")
                        for k, v in entry.metadata.items():
                            logger.info(f"  {k}: {v}")
                else:
                    logger.info("Context entry not found.")
        
        elif choice == "3":
            # List all keys
            keys = await context_manager.list_all_keys()
            logger.info(f"\n📋 All Context Keys ({len(keys)}):")
            for i, key in enumerate(keys, 1):
                logger.info(f"{i}. {key}")
        
        elif choice == "4":
            # Exit
            logger.info("\n👋 Goodbye!")
            break
        
        else:
            logger.warning("Invalid choice. Please enter 1-4.")
    
    logger.info("\n" + "=" * 60)
    logger.info("✓ Example completed successfully!")


if __name__ == "__main__":
    asyncio.run(main())

# Made with Bob
