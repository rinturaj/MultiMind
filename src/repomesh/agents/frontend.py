"""
Frontend agent for analyzing frontend repositories.

This module provides specialized analysis for frontend codebases,
including component detection, UI patterns, and API integration tracking.
"""

from typing import Any, Dict, List
from pathlib import Path

from repomesh.agents.base import BaseAgent
from repomesh.core.events import EventBus
from repomesh.core.exceptions import AgentExecutionError
from repomesh.core.models import AgentType, EventType, RepoMetadata, Task
from repomesh.context.manager import SharedContextManager


class FrontendAgent(BaseAgent):
    """Agent specialized in frontend repository analysis."""

    def __init__(
        self,
        context_manager: SharedContextManager,
        event_bus: EventBus,
        llm_client: Any = None,
    ) -> None:
        """Initialize the frontend agent.

        Args:
            context_manager: Shared context manager
            event_bus: Event bus for communication
            llm_client: Optional LLM client for advanced analysis
        """
        super().__init__(AgentType.FRONTEND, context_manager, event_bus)
        self.llm_client = llm_client

    async def process_task(
        self,
        task: Task,
        repo_metadata: RepoMetadata,
    ) -> Dict[str, Any]:
        """Process a frontend analysis task.

        Args:
            task: Task to process
            repo_metadata: Repository metadata

        Returns:
            Task result dictionary
        """
        try:
            await self.publish_event(
                EventType.AGENT_STARTED,
                {"task_id": str(task.id)},
                repo_id=task.repo_id,
                task_id=task.id,
            )

            # Analyze components
            components = await self._analyze_components(repo_metadata)

            # Detect UI patterns
            ui_patterns = await self._detect_ui_patterns(repo_metadata)

            # Track API integrations
            api_integrations = await self._track_api_integrations(repo_metadata)

            # Store findings in context
            await self._store_findings(repo_metadata, components, ui_patterns, api_integrations)

            result = {
                "components": components,
                "ui_patterns": ui_patterns,
                "api_integrations": api_integrations,
                "summary": self._generate_summary(components, ui_patterns, api_integrations),
            }

            await self.publish_event(
                EventType.AGENT_COMPLETED,
                {"task_id": str(task.id), "result": result},
                repo_id=task.repo_id,
                task_id=task.id,
            )

            return result

        except Exception as e:
            await self.publish_event(
                EventType.AGENT_FAILED,
                {"task_id": str(task.id), "error": str(e)},
                repo_id=task.repo_id,
                task_id=task.id,
            )
            raise AgentExecutionError(self.agent_type.value, str(e))

    async def _analyze_components(self, repo_metadata: RepoMetadata) -> List[Dict[str, Any]]:
        """Analyze frontend components.

        Args:
            repo_metadata: Repository metadata

        Returns:
            List of component information
        """
        components = []

        # Get component files (React, Vue, etc.)
        component_extensions = [".jsx", ".tsx", ".vue", ".svelte"]
        component_files = self._get_files_by_extension(repo_metadata, component_extensions)

        for file in component_files[:50]:  # Limit to first 50 components
            component_name = Path(file.path).stem
            component_info = {
                "name": component_name,
                "path": file.path,
                "type": self._detect_component_type(file.extension),
                "lines": file.lines or 0,
            }
            components.append(component_info)

        return components

    def _detect_component_type(self, extension: str) -> str:
        """Detect component type from extension.

        Args:
            extension: File extension

        Returns:
            Component type
        """
        type_map = {
            ".jsx": "React",
            ".tsx": "React TypeScript",
            ".vue": "Vue",
            ".svelte": "Svelte",
        }
        return type_map.get(extension.lower(), "Unknown")

    async def _detect_ui_patterns(self, repo_metadata: RepoMetadata) -> List[str]:
        """Detect UI patterns and libraries.

        Args:
            repo_metadata: Repository metadata

        Returns:
            List of detected UI patterns
        """
        patterns = []

        # Check dependencies for UI libraries
        deps = repo_metadata.dependencies
        ui_libraries = {
            "material-ui": "Material-UI",
            "@mui/material": "Material-UI",
            "antd": "Ant Design",
            "bootstrap": "Bootstrap",
            "tailwindcss": "Tailwind CSS",
            "styled-components": "Styled Components",
            "emotion": "Emotion",
            "chakra-ui": "Chakra UI",
            "semantic-ui": "Semantic UI",
        }

        for dep_key, pattern_name in ui_libraries.items():
            if any(dep_key in dep.lower() for dep in deps.keys()):
                patterns.append(pattern_name)

        # Check for CSS frameworks
        css_files = self._get_files_by_extension(repo_metadata, [".css", ".scss", ".sass"])
        if css_files:
            patterns.append("Custom CSS")

        return patterns

    async def _track_api_integrations(self, repo_metadata: RepoMetadata) -> List[Dict[str, Any]]:
        """Track API integrations in frontend code.

        Args:
            repo_metadata: Repository metadata

        Returns:
            List of API integration information
        """
        integrations = []

        # Check for common API client libraries
        deps = repo_metadata.dependencies
        api_clients = {
            "axios": "Axios HTTP Client",
            "fetch": "Fetch API",
            "apollo-client": "Apollo GraphQL",
            "@tanstack/react-query": "React Query",
            "swr": "SWR",
        }

        for client_key, client_name in api_clients.items():
            if any(client_key in dep.lower() for dep in deps.keys()):
                integrations.append({
                    "client": client_name,
                    "type": "HTTP" if "http" in client_key.lower() else "GraphQL" if "graphql" in client_key.lower() else "Data Fetching",
                })

        return integrations

    async def _store_findings(
        self,
        repo_metadata: RepoMetadata,
        components: List[Dict[str, Any]],
        ui_patterns: List[str],
        api_integrations: List[Dict[str, Any]],
    ) -> None:
        """Store analysis findings in shared context.

        Args:
            repo_metadata: Repository metadata
            components: Component information
            ui_patterns: UI patterns
            api_integrations: API integrations
        """
        # Store component information
        component_summary = f"Found {len(components)} components\n"
        component_summary += "\n".join([f"- {c['name']} ({c['type']})" for c in components[:10]])

        await self.context_manager.store_component_info(
            content=component_summary,
            repo_id=repo_metadata.id,
            agent_type=self.agent_type,
            component_name="frontend_components",
            metadata={"count": len(components)},
        )

        # Store UI patterns
        if ui_patterns:
            patterns_summary = "UI Patterns:\n" + "\n".join([f"- {p}" for p in ui_patterns])
            await self.store_context(
                key=f"ui_patterns:{repo_metadata.id}",
                content=patterns_summary,
                repo_id=repo_metadata.id,
                metadata={"patterns": ui_patterns},
            )

        # Store API integrations
        if api_integrations:
            api_summary = "API Integrations:\n" + "\n".join([f"- {i['client']}" for i in api_integrations])
            await self.store_context(
                key=f"api_integrations:{repo_metadata.id}",
                content=api_summary,
                repo_id=repo_metadata.id,
                metadata={"integrations": api_integrations},
            )

    def _generate_summary(
        self,
        components: List[Dict[str, Any]],
        ui_patterns: List[str],
        api_integrations: List[Dict[str, Any]],
    ) -> str:
        """Generate a summary of frontend analysis.

        Args:
            components: Component information
            ui_patterns: UI patterns
            api_integrations: API integrations

        Returns:
            Summary string
        """
        summary_parts = [
            f"Frontend Analysis Summary:",
            f"- Components: {len(components)}",
            f"- UI Patterns: {', '.join(ui_patterns) if ui_patterns else 'None detected'}",
            f"- API Clients: {len(api_integrations)}",
        ]
        return "\n".join(summary_parts)

    def get_capabilities(self) -> Dict[str, Any]:
        """Get frontend agent capabilities.

        Returns:
            Dictionary describing capabilities
        """
        return {
            "agent_type": self.agent_type.value,
            "supported_repo_types": ["frontend", "fullstack"],
            "supported_tasks": [
                "component_analysis",
                "ui_pattern_detection",
                "api_integration_tracking",
            ],
            "max_concurrent_tasks": 3,
            "requires_llm": False,
        }

# Made with Bob
