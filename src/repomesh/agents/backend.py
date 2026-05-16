"""
Backend agent for analyzing backend repositories.

This module provides specialized analysis for backend codebases,
including API endpoint extraction, schema tracking, and service dependencies.
"""

from typing import Any, Dict, List
from pathlib import Path

from repomesh.agents.base import BaseAgent
from repomesh.core.events import EventBus
from repomesh.core.exceptions import AgentExecutionError
from repomesh.core.models import AgentType, EventType, RepoMetadata, Task
from repomesh.context.manager import SharedContextManager


class BackendAgent(BaseAgent):
    """Agent specialized in backend repository analysis."""

    def __init__(
        self,
        context_manager: SharedContextManager,
        event_bus: EventBus,
        llm_client: Any = None,
    ) -> None:
        """Initialize the backend agent.

        Args:
            context_manager: Shared context manager
            event_bus: Event bus for communication
            llm_client: Optional LLM client for advanced analysis
        """
        super().__init__(AgentType.BACKEND, context_manager, event_bus)
        self.llm_client = llm_client

    async def process_task(
        self,
        task: Task,
        repo_metadata: RepoMetadata,
    ) -> Dict[str, Any]:
        """Process a backend analysis task.

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

            # Extract API endpoints
            endpoints = await self._extract_api_endpoints(repo_metadata)

            # Track database schemas
            schemas = await self._track_database_schemas(repo_metadata)

            # Map service dependencies
            dependencies = await self._map_service_dependencies(repo_metadata)

            # Store findings in context
            await self._store_findings(repo_metadata, endpoints, schemas, dependencies)

            result = {
                "endpoints": endpoints,
                "schemas": schemas,
                "dependencies": dependencies,
                "summary": self._generate_summary(endpoints, schemas, dependencies),
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

    async def _extract_api_endpoints(self, repo_metadata: RepoMetadata) -> List[Dict[str, Any]]:
        """Extract API endpoints from backend code.

        Args:
            repo_metadata: Repository metadata

        Returns:
            List of endpoint information
        """
        endpoints = []

        # Detect framework
        framework = self._detect_framework(repo_metadata)

        # Get relevant files based on framework
        if framework in ["FastAPI", "Flask", "Django"]:
            py_files = self._get_code_files(repo_metadata, "Python")
            endpoints.extend(self._extract_python_endpoints(py_files, framework))
        elif framework in ["Express", "NestJS"]:
            js_files = self._get_code_files(repo_metadata, "JavaScript")
            ts_files = self._get_code_files(repo_metadata, "TypeScript")
            endpoints.extend(self._extract_js_endpoints(js_files + ts_files, framework))
        elif framework == "Spring":
            java_files = self._get_code_files(repo_metadata, "Java")
            endpoints.extend(self._extract_java_endpoints(java_files))

        return endpoints

    def _detect_framework(self, repo_metadata: RepoMetadata) -> str:
        """Detect backend framework.

        Args:
            repo_metadata: Repository metadata

        Returns:
            Framework name
        """
        deps = repo_metadata.dependencies
        tech_stack = repo_metadata.tech_stack

        # Check dependencies and tech stack
        if "fastapi" in deps or "FastAPI" in tech_stack:
            return "FastAPI"
        elif "flask" in deps or "Flask" in tech_stack:
            return "Flask"
        elif "django" in deps or "Django" in tech_stack:
            return "Django"
        elif "express" in deps or "Express" in tech_stack:
            return "Express"
        elif "@nestjs/core" in deps or "NestJS" in tech_stack:
            return "NestJS"
        elif "spring" in str(deps).lower() or "Spring" in tech_stack:
            return "Spring"
        else:
            return "Unknown"

    def _extract_python_endpoints(self, files: List[Any], framework: str) -> List[Dict[str, Any]]:
        """Extract endpoints from Python files.

        Args:
            files: List of Python files
            framework: Framework name

        Returns:
            List of endpoints
        """
        endpoints = []
        
        # Simple heuristic: look for common route patterns
        route_patterns = ["@app.route", "@router.", "@api_view", "path("]
        
        for file in files[:20]:  # Limit to first 20 files
            endpoints.append({
                "file": file.path,
                "framework": framework,
                "type": "REST API",
                "estimated_count": 1,  # Placeholder
            })

        return endpoints

    def _extract_js_endpoints(self, files: List[Any], framework: str) -> List[Dict[str, Any]]:
        """Extract endpoints from JavaScript/TypeScript files.

        Args:
            files: List of JS/TS files
            framework: Framework name

        Returns:
            List of endpoints
        """
        endpoints = []
        
        for file in files[:20]:  # Limit to first 20 files
            if "route" in file.path.lower() or "controller" in file.path.lower():
                endpoints.append({
                    "file": file.path,
                    "framework": framework,
                    "type": "REST API",
                    "estimated_count": 1,  # Placeholder
                })

        return endpoints

    def _extract_java_endpoints(self, files: List[Any]) -> List[Dict[str, Any]]:
        """Extract endpoints from Java files.

        Args:
            files: List of Java files

        Returns:
            List of endpoints
        """
        endpoints = []
        
        for file in files[:20]:  # Limit to first 20 files
            if "controller" in file.path.lower():
                endpoints.append({
                    "file": file.path,
                    "framework": "Spring",
                    "type": "REST API",
                    "estimated_count": 1,  # Placeholder
                })

        return endpoints

    async def _track_database_schemas(self, repo_metadata: RepoMetadata) -> List[Dict[str, Any]]:
        """Track database schemas.

        Args:
            repo_metadata: Repository metadata

        Returns:
            List of schema information
        """
        schemas = []

        # Look for migration files
        migration_patterns = ["migrations", "migrate", "schema"]
        for file in repo_metadata.files:
            if any(pattern in file.path.lower() for pattern in migration_patterns):
                schemas.append({
                    "file": file.path,
                    "type": "Migration",
                })

        # Look for ORM models
        model_patterns = ["models.py", "model.ts", "entity.java"]
        for file in repo_metadata.files:
            if any(pattern in file.path.lower() for pattern in model_patterns):
                schemas.append({
                    "file": file.path,
                    "type": "ORM Model",
                })

        return schemas[:20]  # Limit results

    async def _map_service_dependencies(self, repo_metadata: RepoMetadata) -> List[Dict[str, Any]]:
        """Map service dependencies.

        Args:
            repo_metadata: Repository metadata

        Returns:
            List of service dependencies
        """
        dependencies = []

        # Check for database dependencies
        db_deps = {
            "postgresql": "PostgreSQL",
            "mysql": "MySQL",
            "mongodb": "MongoDB",
            "redis": "Redis",
            "sqlite": "SQLite",
        }

        for dep_key, db_name in db_deps.items():
            if any(dep_key in dep.lower() for dep in repo_metadata.dependencies.keys()):
                dependencies.append({
                    "name": db_name,
                    "type": "Database",
                })

        # Check for message queue dependencies
        mq_deps = {
            "celery": "Celery",
            "rabbitmq": "RabbitMQ",
            "kafka": "Kafka",
        }

        for dep_key, mq_name in mq_deps.items():
            if any(dep_key in dep.lower() for dep in repo_metadata.dependencies.keys()):
                dependencies.append({
                    "name": mq_name,
                    "type": "Message Queue",
                })

        return dependencies

    async def _store_findings(
        self,
        repo_metadata: RepoMetadata,
        endpoints: List[Dict[str, Any]],
        schemas: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]],
    ) -> None:
        """Store analysis findings in shared context.

        Args:
            repo_metadata: Repository metadata
            endpoints: Endpoint information
            schemas: Schema information
            dependencies: Service dependencies
        """
        # Store API endpoints
        if endpoints:
            endpoint_summary = f"Found {len(endpoints)} API endpoints\n"
            endpoint_summary += "\n".join([f"- {e['file']} ({e['framework']})" for e in endpoints[:10]])

            await self.context_manager.store_api_contract(
                content=endpoint_summary,
                repo_id=repo_metadata.id,
                agent_type=self.agent_type,
                endpoint="backend_api",
                metadata={"count": len(endpoints)},
            )

        # Store schemas
        if schemas:
            schema_summary = f"Found {len(schemas)} schema files\n"
            schema_summary += "\n".join([f"- {s['file']} ({s['type']})" for s in schemas[:10]])

            await self.context_manager.store_schema_change(
                content=schema_summary,
                repo_id=repo_metadata.id,
                agent_type=self.agent_type,
                schema_name="database_schemas",
                metadata={"count": len(schemas)},
            )

        # Store dependencies
        if dependencies:
            dep_summary = "Service Dependencies:\n" + "\n".join([f"- {d['name']} ({d['type']})" for d in dependencies])
            await self.context_manager.store_dependency_info(
                content=dep_summary,
                repo_id=repo_metadata.id,
                agent_type=self.agent_type,
                dependency_type="services",
                metadata={"dependencies": dependencies},
            )

    def _generate_summary(
        self,
        endpoints: List[Dict[str, Any]],
        schemas: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]],
    ) -> str:
        """Generate a summary of backend analysis.

        Args:
            endpoints: Endpoint information
            schemas: Schema information
            dependencies: Service dependencies

        Returns:
            Summary string
        """
        summary_parts = [
            f"Backend Analysis Summary:",
            f"- API Endpoints: {len(endpoints)}",
            f"- Database Schemas: {len(schemas)}",
            f"- Service Dependencies: {len(dependencies)}",
        ]
        return "\n".join(summary_parts)

    def get_capabilities(self) -> Dict[str, Any]:
        """Get backend agent capabilities.

        Returns:
            Dictionary describing capabilities
        """
        return {
            "agent_type": self.agent_type.value,
            "supported_repo_types": ["backend", "fullstack"],
            "supported_tasks": [
                "api_endpoint_extraction",
                "schema_tracking",
                "service_dependency_mapping",
            ],
            "max_concurrent_tasks": 3,
            "requires_llm": False,
        }

# Made with Bob
