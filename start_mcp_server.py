#!/usr/bin/env python3
"""
Startup script for RepoMesh MCP Server.

This script initializes and runs the MCP server, making the multi-agent
repository analysis system available as MCP tools.
"""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Check for OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key.startswith("sk-proj-XXX"):
    print("=" * 70)
    print("WARNING: OpenAI API key not configured!")
    print("=" * 70)
    print("\nPlease set your OpenAI API key in the .env file:")
    print("  1. Open the .env file in the project root")
    print("  2. Replace 'your_openai_api_key_here' with your actual API key")
    print("  3. Save the file and restart the server")
    print("\nThe server will start, but AI-powered features may not work.")
    print("=" * 70)
    print()

# Import and run the MCP server

if __name__ == "__main__":
    print("Starting RepoMesh MCP Server...")
    print("=" * 70)
    print("Available MCP Tools:")
    print("  - register_repository: Clone and register a Git repository")
    print("  - load_local_repository: Load an existing local repository")
    print("  - list_repositories: List all registered repositories")
    print("  - get_repository_details: Get detailed repo information")
    print("  - analyze_frontend: Run frontend agent analysis")
    print("  - analyze_backend: Run backend agent analysis")
    print("  - run_full_analysis: Run complete multi-agent orchestration")
    print("  - search_shared_context: Search across agent findings")
    print("  - store_architecture_note: Store architectural decisions")
    print("  - get_agent_capabilities: Get agent capabilities")
    print("  - list_available_agents: List all available agents")
    print("=" * 70)
    print()
    
    from repomesh.mcp_server import mcp
    mcp.run(transport='stdio')

# Made with Bob
