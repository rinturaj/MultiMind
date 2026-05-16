#!/usr/bin/env python3
"""
Test script for RepoMesh MCP Server.

This script verifies that the MCP server can start and basic functionality works.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    try:
        from repomesh.agents.registry import AgentRegistry
        from repomesh.context.manager import SharedContextManager
        from repomesh.context.store import InMemoryStore
        from repomesh.core.events import EventBus
        from repomesh.orchestrator.workflow import OrchestrationWorkflow
        from repomesh.repos.manager import RepoManager
        from repomesh.core.models import AgentType
        print("✓ All core imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_initialization():
    """Test that services can be initialized."""
    print("\nTesting service initialization...")
    try:
        from repomesh.repos.manager import RepoManager
        from repomesh.core.events import EventBus
        from repomesh.context.store import InMemoryStore
        from repomesh.context.manager import SharedContextManager
        from repomesh.agents.registry import AgentRegistry
        
        repo_manager = RepoManager()
        event_bus = EventBus()
        context_store = InMemoryStore()
        context_manager = SharedContextManager(context_store, event_bus)
        agent_registry = AgentRegistry(context_manager, event_bus)
        
        print("✓ All services initialized successfully")
        return True
    except Exception as e:
        print(f"✗ Initialization failed: {e}")
        return False

def test_agent_registry():
    """Test agent registry functionality."""
    print("\nTesting agent registry...")
    try:
        from repomesh.repos.manager import RepoManager
        from repomesh.core.events import EventBus
        from repomesh.context.store import InMemoryStore
        from repomesh.context.manager import SharedContextManager
        from repomesh.agents.registry import AgentRegistry
        from repomesh.core.models import AgentType
        
        repo_manager = RepoManager()
        event_bus = EventBus()
        context_store = InMemoryStore()
        context_manager = SharedContextManager(context_store, event_bus)
        agent_registry = AgentRegistry(context_manager, event_bus)
        
        # Test listing agents
        agents = agent_registry.list_agents()
        print(f"  Registered agents: {[a.value for a in agents]}")
        
        # Test getting capabilities
        for agent_type in agents:
            caps = agent_registry.get_capabilities(agent_type)
            print(f"  {agent_type.value} capabilities: {caps.get('supported_tasks', [])}")
        
        print("✓ Agent registry working correctly")
        return True
    except Exception as e:
        print(f"✗ Agent registry test failed: {e}")
        return False

def test_mcp_server():
    """Test that MCP server can be imported."""
    print("\nTesting MCP server...")
    try:
        from repomesh import mcp_server
        print("✓ MCP server module loaded successfully")
        print(f"  Server name: RepoMesh AI - Multi-Agent Repository Analysis")
        return True
    except Exception as e:
        print(f"✗ MCP server test failed: {e}")
        return False

def check_api_key():
    """Check if OpenAI API key is configured."""
    print("\nChecking API key configuration...")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your_openai_api_key_here":
        print("⚠ OpenAI API key not configured in .env file")
        print("  The server will start but AI features may not work")
        return False
    else:
        print(f"✓ OpenAI API key configured (starts with: {api_key[:10]}...)")
        return True

def main():
    """Run all tests."""
    print("=" * 70)
    print("RepoMesh MCP Server - Test Suite")
    print("=" * 70)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("Initialization", test_initialization()))
    results.append(("Agent Registry", test_agent_registry()))
    results.append(("MCP Server", test_mcp_server()))
    results.append(("API Key", check_api_key()))
    
    print("\n" + "=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    all_passed = all(result[1] for result in results[:-1])  # Exclude API key check
    
    print("=" * 70)
    if all_passed:
        print("✓ All critical tests passed!")
        print("\nYou can now start the MCP server with:")
        print("  python start_mcp_server.py")
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

# Made with Bob
