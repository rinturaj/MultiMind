# RepoMesh AI - Technical Specification

## Executive Summary

RepoMesh AI is a multi-agent AI orchestration platform designed to coordinate development activities across multiple repositories using shared context and intelligent agents. This document provides detailed technical specifications for Phase 1 implementation.

## System Requirements

### Runtime Environment
- **Python**: 3.11+ (required for latest type hints and performance)
- **Operating System**: Linux, macOS, Windows (WSL2)
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 10GB free space for repositories and vector store

### External Dependencies
- **Git**: 2.30+ (for GitPython operations)
- **OpenAI API**: Valid API key with GPT-4 access
- **ChromaDB**: Optional, for persistent vector storage

## Architecture Components

### 1. API Layer (FastAPI)

#### Technology Stack
- **Framework**: FastAPI 0.109+
- **ASGI Server**: Uvicorn with uvloop
- **Validation**: Pydantic 2.5+
- **HTTP Client**: httpx for async requests

#### Endpoints Specification

##### Health Check
```
GET /health
Response: 200 OK
{
  "status": "healthy",
  "version": "0.1.0",
  "timestamp": "2026-05-16T03:20:00Z",
  "services": {
    "repo_manager": "operational",
    "context_manager": "operational",
    "orchestrator": "operational"
  }
}
```

##### Register Repository
```
POST /api/v1/repos/register
Content-Type: application/json

Request:
{
  "remote_url": "https://github.com/user/repo.git",  // Optional
  "local_path": "/path/to/repo",                     // Optional
  "dest_path": "/workspace/repos/repo-name",         // Required if remote_url
  "branch": "main"                                   // Optional, default: main
}

Response: 201 Created
{
  "repo_id": "uuid-v4",
  "name": "repo-name",
  "type": "frontend",
  "path": "/workspace/repos/repo-name",
  "remote_url": "https://github.com/user/repo.git",
  "files": [
    {
      "path": "src/App.tsx",
      "size": 1024,
      "extension": ".tsx",
      "is_code": true
    }
  ],
  "summary": "React TypeScript application with...",
  "dependencies": ["react", "typescript"],
  "tech_stack": ["react", "typescript", "vite"],
  "created_at": "2026-05-16T03:20:00Z",
  "updated_at": "2026-05-16T03:20:00Z"
}
```

##### Trigger Orchestration
```
POST /api/v1/orchestrate
Content-Type: application/json

Request:
{
  "repo_ids": ["uuid-1", "uuid-2"],
  "task_description": "Analyze API contracts and ensure consistency",
  "options": {
    "parallel_execution": true,
    "max_iterations": 5
  }
}

Response: 202 Accepted
{
  "orchestration_id": "uuid-v4",
  "status": "in_progress",
  "repos": ["uuid-1", "uuid-2"],
  "tasks": [
    {
      "task_id": "task-1",
      "repo_id": "uuid-1",
      "agent_type": "frontend",
      "description": "Analyze frontend API integration",
      "status": "pending"
    }
  ],
  "started_at": "2026-05-16T03:20:00Z"
}
```

##### Inspect Context
```
GET /api/v1/context?query=api+contracts&limit=10
Response: 200 OK
{
  "results": [
    {
      "key": "api_contract_user_service",
      "type": "api_contract",
      "content": {
        "endpoint": "/api/users",
        "method": "GET",
        "response_schema": {...}
      },
      "metadata": {
        "source": "backend-agent",
        "repo_id": "uuid-1",
        "timestamp": "2026-05-16T03:20:00Z"
      }
    }
  ],
  "total": 1,
  "query": "api contracts"
}
```

#### Error Handling
```python
class APIError(BaseModel):
    error: str
    detail: str
    timestamp: datetime
    request_id: str

# Standard error responses
400 Bad Request - Invalid input
404 Not Found - Resource not found
409 Conflict - Resource conflict
500 Internal Server Error - Server error
503 Service Unavailable - Service down
```

### 2. Orchestration Layer (LangGraph)

#### State Graph Definition

```python
from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END

class OrchestrationState(TypedDict):
    """Complete state for orchestration workflow"""
    # Repository information
    repos: List[RepoMetadata]
    
    # Task management
    tasks: List[Task]
    task_results: Dict[str, TaskResult]
    
    # Dependency tracking
    dependencies: Dict[str, List[str]]
    
    # Shared context
    shared_context: Dict[str, Any]
    architecture_notes: List[str]
    api_contracts: Dict[str, Any]
    schema_changes: List[Dict]
    
    # Event tracking
    events: List[Event]
    
    # Execution metadata
    status: str  # "started", "in_progress", "completed", "failed"
    current_step: str
    iteration: int
    max_iterations: int
    started_at: datetime
    completed_at: Optional[datetime]
    
    # Error handling
    errors: List[str]
```

#### Node Implementations

##### Planner Node
```python
async def planner_node(state: OrchestrationState) -> OrchestrationState:
    """
    Analyze repositories and create execution plan
    
    Steps:
    1. Analyze each repository's structure and type
    2. Identify cross-repository dependencies
    3. Create prioritized task list
    4. Assign tasks to appropriate agents
    5. Set up dependency graph
    
    Returns:
        Updated state with tasks and dependencies
    """
    logger.info("Starting planner node")
    
    tasks = []
    dependencies = {}
    
    for repo in state["repos"]:
        # Determine agent type based on repo type
        agent_type = determine_agent_type(repo.type)
        
        # Create analysis task
        task = Task(
            task_id=f"analyze_{repo.repo_id}",
            repo_id=repo.repo_id,
            agent_type=agent_type,
            description=f"Analyze {repo.name} repository",
            dependencies=[],
            status=TaskStatus.PENDING,
            context={"repo_metadata": repo.dict()}
        )
        tasks.append(task)
    
    # Identify cross-repo dependencies
    dependencies = identify_dependencies(state["repos"])
    
    state["tasks"] = tasks
    state["dependencies"] = dependencies
    state["current_step"] = "task_distributor"
    
    logger.info(f"Created {len(tasks)} tasks with {len(dependencies)} dependencies")
    return state
```

##### Task Distributor Node
```python
async def task_distributor_node(state: OrchestrationState) -> OrchestrationState:
    """
    Distribute tasks to agents for parallel execution
    
    Steps:
    1. Group tasks by agent type
    2. Check dependencies
    3. Mark tasks ready for execution
    4. Route to appropriate agent nodes
    
    Returns:
        Updated state with task assignments
    """
    logger.info("Starting task distributor")
    
    # Group tasks by agent type
    frontend_tasks = [t for t in state["tasks"] if t.agent_type == "frontend"]
    backend_tasks = [t for t in state["tasks"] if t.agent_type == "backend"]
    
    # Update task status
    for task in state["tasks"]:
        if not task.dependencies:
            task.status = TaskStatus.IN_PROGRESS
    
    state["current_step"] = "agent_execution"
    
    logger.info(f"Distributed {len(frontend_tasks)} frontend, {len(backend_tasks)} backend tasks")
    return state
```

##### Agent Execution Nodes
```python
async def frontend_agent_node(state: OrchestrationState) -> OrchestrationState:
    """Execute frontend agent tasks"""
    logger.info("Starting frontend agent execution")
    
    agent = FrontendAgent(
        agent_id="frontend-agent-1",
        context_manager=get_context_manager(),
        event_bus=get_event_bus(),
        llm_client=get_llm_client()
    )
    
    frontend_tasks = [t for t in state["tasks"] if t.agent_type == "frontend"]
    
    for task in frontend_tasks:
        if task.status == TaskStatus.IN_PROGRESS:
            repo = next(r for r in state["repos"] if r.repo_id == task.repo_id)
            result = await agent.process_task(task, repo)
            
            state["task_results"][task.task_id] = result
            task.status = TaskStatus.COMPLETED
            
            # Publish completion event
            event = Event(
                event_id=generate_id(),
                event_type=EventType.TASK_COMPLETE,
                source="frontend-agent",
                timestamp=datetime.utcnow(),
                payload={"task_id": task.task_id, "result": result.dict()}
            )
            state["events"].append(event)
    
    return state

async def backend_agent_node(state: OrchestrationState) -> OrchestrationState:
    """Execute backend agent tasks"""
    # Similar implementation to frontend_agent_node
    pass
```

##### Context Sync Node
```python
async def context_sync_node(state: OrchestrationState) -> OrchestrationState:
    """
    Synchronize shared context across all agents
    
    Steps:
    1. Collect context updates from all agents
    2. Resolve any conflicts
    3. Update shared context store
    4. Notify agents of updates
    
    Returns:
        Updated state with synchronized context
    """
    logger.info("Starting context synchronization")
    
    context_manager = get_context_manager()
    
    # Collect all context updates from task results
    for task_id, result in state["task_results"].items():
        if result.context_updates:
            for key, value in result.context_updates.items():
                await context_manager.store(key, value, {
                    "source": result.agent_id,
                    "task_id": task_id,
                    "timestamp": datetime.utcnow()
                })
    
    # Update state
    state["current_step"] = "completed"
    state["status"] = "completed"
    state["completed_at"] = datetime.utcnow()
    
    logger.info("Context synchronization complete")
    return state
```

#### Conditional Routing
```python
def route_to_agents(state: OrchestrationState) -> List[str]:
    """
    Determine which agent nodes to execute
    
    Returns:
        List of node names to execute in parallel
    """
    nodes = []
    
    has_frontend = any(t.agent_type == "frontend" for t in state["tasks"])
    has_backend = any(t.agent_type == "backend" for t in state["tasks"])
    
    if has_frontend:
        nodes.append("frontend_agent")
    if has_backend:
        nodes.append("backend_agent")
    
    return nodes
```

### 3. Agent System

#### BaseAgent Abstract Class

```python
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseAgent(ABC):
    """
    Abstract base class for all agents
    
    Provides common functionality:
    - Context access
    - Event publishing
    - LLM interaction
    - Task processing interface
    """
    
    def __init__(
        self,
        agent_id: str,
        context_manager: SharedContextManager,
        event_bus: EventBus,
        llm_client: Any
    ):
        self.agent_id = agent_id
        self.context_manager = context_manager
        self.event_bus = event_bus
        self.llm_client = llm_client
        self.logger = logging.getLogger(f"agent.{agent_id}")
    
    @abstractmethod
    async def process_task(self, task: Task, repo: RepoMetadata) -> TaskResult:
        """
        Process assigned task
        
        Args:
            task: Task to process
            repo: Repository metadata
            
        Returns:
            TaskResult with outcomes and context updates
        """
        pass
    
    @abstractmethod
    async def get_capabilities(self) -> List[str]:
        """
        Return list of agent capabilities
        
        Returns:
            List of capability strings
        """
        pass
    
    async def get_context(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Retrieve relevant context from shared memory
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            List of context items
        """
        return await self.context_manager.search(query, limit)
    
    async def publish_event(self, event: Event) -> None:
        """
        Publish event to event bus
        
        Args:
            event: Event to publish
        """
        await self.event_bus.publish(event)
        self.logger.info(f"Published event: {event.event_type}")
    
    async def call_llm(self, prompt: str, **kwargs) -> str:
        """
        Call LLM with prompt
        
        Args:
            prompt: Prompt text
            **kwargs: Additional LLM parameters
            
        Returns:
            LLM response text
        """
        response = await self.llm_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            **kwargs
        )
        return response.choices[0].message.content
```

#### FrontendAgent Implementation

```python
class FrontendAgent(BaseAgent):
    """
    Agent specialized for frontend repositories
    
    Capabilities:
    - Component analysis
    - API integration detection
    - UI pattern recognition
    - Dependency tracking
    """
    
    async def process_task(self, task: Task, repo: RepoMetadata) -> TaskResult:
        """
        Process frontend-specific task
        
        Steps:
        1. Analyze component structure
        2. Identify API integration points
        3. Extract UI patterns
        4. Check for API contract compliance
        5. Generate recommendations
        """
        self.logger.info(f"Processing task {task.task_id} for repo {repo.name}")
        
        # Get relevant API contracts from shared context
        api_contracts = await self.get_context("api contracts")
        
        # Analyze repository structure
        analysis = await self._analyze_frontend_structure(repo)
        
        # Check API integration
        api_integration = await self._check_api_integration(repo, api_contracts)
        
        # Generate recommendations
        recommendations = await self._generate_recommendations(
            repo, analysis, api_integration
        )
        
        # Publish UI patterns to shared context
        await self.context_manager.store(
            f"ui_patterns_{repo.repo_id}",
            analysis["ui_patterns"],
            {"source": self.agent_id, "repo_id": repo.repo_id}
        )
        
        # Publish completion event
        await self.publish_event(Event(
            event_id=generate_id(),
            event_type=EventType.TASK_COMPLETE,
            source=self.agent_id,
            timestamp=datetime.utcnow(),
            payload={"task_id": task.task_id, "status": "completed"}
        ))
        
        return TaskResult(
            task_id=task.task_id,
            agent_id=self.agent_id,
            status="completed",
            output=recommendations,
            context_updates={
                f"ui_patterns_{repo.repo_id}": analysis["ui_patterns"]
            }
        )
    
    async def get_capabilities(self) -> List[str]:
        return [
            "component_analysis",
            "api_integration_detection",
            "ui_pattern_recognition",
            "dependency_tracking",
            "accessibility_check"
        ]
    
    async def _analyze_frontend_structure(self, repo: RepoMetadata) -> Dict:
        """Analyze frontend repository structure"""
        # Implementation details
        pass
    
    async def _check_api_integration(
        self, repo: RepoMetadata, api_contracts: List[Dict]
    ) -> Dict:
        """Check API integration compliance"""
        # Implementation details
        pass
    
    async def _generate_recommendations(
        self, repo: RepoMetadata, analysis: Dict, api_integration: Dict
    ) -> str:
        """Generate architectural recommendations"""
        prompt = f"""
        Analyze this frontend repository and provide recommendations:
        
        Repository: {repo.name}
        Tech Stack: {', '.join(repo.tech_stack)}
        
        Structure Analysis:
        {json.dumps(analysis, indent=2)}
        
        API Integration:
        {json.dumps(api_integration, indent=2)}
        
        Provide:
        1. Architecture assessment
        2. API integration recommendations
        3. Potential improvements
        """
        
        return await self.call_llm(prompt)
```

#### BackendAgent Implementation

```python
class BackendAgent(BaseAgent):
    """
    Agent specialized for backend repositories
    
    Capabilities:
    - API endpoint analysis
    - Schema tracking
    - Service dependency mapping
    - Endpoint documentation
    """
    
    async def process_task(self, task: Task, repo: RepoMetadata) -> TaskResult:
        """
        Process backend-specific task
        
        Steps:
        1. Extract API endpoints
        2. Analyze database schemas
        3. Map service dependencies
        4. Generate API contracts
        5. Publish to shared context
        """
        self.logger.info(f"Processing task {task.task_id} for repo {repo.name}")
        
        # Extract API endpoints
        endpoints = await self._extract_api_endpoints(repo)
        
        # Analyze database schemas
        schemas = await self._analyze_schemas(repo)
        
        # Map dependencies
        dependencies = await self._map_dependencies(repo)
        
        # Generate API contracts
        api_contracts = await self._generate_api_contracts(endpoints, schemas)
        
        # Publish to shared context
        await self.context_manager.store(
            f"api_contracts_{repo.repo_id}",
            api_contracts,
            {"source": self.agent_id, "repo_id": repo.repo_id}
        )
        
        # Publish schema changes event
        if schemas:
            await self.publish_event(Event(
                event_id=generate_id(),
                event_type=EventType.SCHEMA_CHANGE,
                source=self.agent_id,
                timestamp=datetime.utcnow(),
                payload={"repo_id": repo.repo_id, "schemas": schemas}
            ))
        
        return TaskResult(
            task_id=task.task_id,
            agent_id=self.agent_id,
            status="completed",
            output={"endpoints": endpoints, "schemas": schemas},
            context_updates={
                f"api_contracts_{repo.repo_id}": api_contracts
            }
        )
    
    async def get_capabilities(self) -> List[str]:
        return [
            "api_endpoint_analysis",
            "schema_tracking",
            "service_dependency_mapping",
            "endpoint_documentation",
            "performance_analysis"
        ]
    
    async def _extract_api_endpoints(self, repo: RepoMetadata) -> List[Dict]:
        """Extract API endpoints from code"""
        # Implementation details
        pass
    
    async def _analyze_schemas(self, repo: RepoMetadata) -> List[Dict]:
        """Analyze database schemas"""
        # Implementation details
        pass
    
    async def _map_dependencies(self, repo: RepoMetadata) -> Dict:
        """Map service dependencies"""
        # Implementation details
        pass
    
    async def _generate_api_contracts(
        self, endpoints: List[Dict], schemas: List[Dict]
    ) -> Dict:
        """Generate API contracts"""
        # Implementation details
        pass
```

### 4. Shared Context System

#### Context Store Interface

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class ContextStore(ABC):
    """Abstract interface for context storage"""
    
    @abstractmethod
    async def store(
        self, key: str, value: Any, metadata: Dict[str, Any]
    ) -> None:
        """
        Store value with metadata
        
        Args:
            key: Unique identifier
            value: Value to store
            metadata: Associated metadata
        """
        pass
    
    @abstractmethod
    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve value by key
        
        Args:
            key: Unique identifier
            
        Returns:
            Dict with value and metadata, or None
        """
        pass
    
    @abstractmethod
    async def search(
        self, query: str, limit: int = 10, filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant context
        
        Args:
            query: Search query
            limit: Maximum results
            filters: Optional metadata filters
            
        Returns:
            List of matching items
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete value by key
        
        Args:
            key: Unique identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def list_keys(self, prefix: str = "") -> List[str]:
        """
        List all keys with optional prefix
        
        Args:
            prefix: Key prefix filter
            
        Returns:
            List of matching keys
        """
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close store and cleanup resources"""
        pass
```

#### In-Memory Store Implementation

```python
class InMemoryStore(ContextStore):
    """
    Simple in-memory context store
    
    Features:
    - Fast access
    - No persistence
    - Substring search
    - Metadata filtering
    """
    
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._lock = asyncio.Lock()
    
    async def store(
        self, key: str, value: Any, metadata: Dict[str, Any]
    ) -> None:
        async with self._lock:
            self._store[key] = {
                "value": value,
                "metadata": metadata,
                "stored_at": datetime.utcnow()
            }
    
    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        return self._store.get(key)
    
    async def search(
        self, query: str, limit: int = 10, filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        results = []
        query_lower = query.lower()
        
        for key, item in self._store.items():
            # Simple substring matching
            value_str = str(item["value"]).lower()
            if query_lower in value_str or query_lower in key.lower():
                # Apply metadata filters if provided
                if filters:
                    if all(
                        item["metadata"].get(k) == v
                        for k, v in filters.items()
                    ):
                        results.append({"key": key, **item})
                else:
                    results.append({"key": key, **item})
        
        return results[:limit]
    
    async def delete(self, key: str) -> bool:
        async with self._lock:
            if key in self._store:
                del self._store[key]
                return True
            return False
    
    async def list_keys(self, prefix: str = "") -> List[str]:
        if prefix:
            return [k for k in self._store.keys() if k.startswith(prefix)]
        return list(self._store.keys())
    
    async def close(self) -> None:
        self._store.clear()
```

#### ChromaDB Store Implementation

```python
import chromadb
from chromadb.config import Settings

class ChromaDBStore(ContextStore):
    """
    ChromaDB-based context store with vector search
    
    Features:
    - Persistent storage
    - Vector similarity search
    - Metadata filtering
    - Embedding generation
    """
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_directory,
            anonymized_telemetry=False
        ))
        self.collection = self.client.get_or_create_collection(
            name="repomesh_context",
            metadata={"description": "RepoMesh shared context"}
        )
    
    async def store(
        self, key: str, value: Any, metadata: Dict[str, Any]
    ) -> None:
        # Convert value to string for embedding
        value_str = json.dumps(value) if not isinstance(value, str) else value
        
        # Add to collection
        self.collection.add(
            ids=[key],
            documents=[value_str],
            metadatas=[{
                **metadata,
                "stored_at": datetime.utcnow().isoformat()
            }]
        )
    
    async def retrieve(self, key: str) -> Optional[Dict[str, Any]]:
        try:
            result = self.collection.get(ids=[key])
            if result["ids"]:
                return {
                    "value": json.loads(result["documents"][0]),
                    "metadata": result["metadatas"][0]
                }
        except Exception:
            return None
    
    async def search(
        self, query: str, limit: int = 10, filters: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        where = filters if filters else None
        
        results = self.collection.query(
            query_texts=[query],
            n_results=limit,
            where=where
        )
        
        items = []
        for i, doc_id in enumerate(results["ids"][0]):
            items.append({
                "key": doc_id,
                "value": json.loads(results["documents"][0][i]),
                "metadata": results["metadatas"][0][i],
                "distance": results["distances"][0][i]
            })
        
        return items
    
    async def delete(self, key: str) -> bool:
        try:
            self.collection.delete(ids=[key])
            return True
        except Exception:
            return False
    
    async def list_keys(self, prefix: str = "") -> List[str]:
        # Get all items
        all_items = self.collection.get()
        keys = all_items["ids"]
        
        if prefix:
            return [k for k in keys if k.startswith(prefix)]
        return keys
    
    async def close(self) -> None:
        # ChromaDB handles persistence automatically
        pass
```

### 5. Event System

```python
from typing import Callable, Dict, List
import asyncio

class EventBus:
    """
    Internal event bus for agent communication
    
    Features:
    - Publish-subscribe pattern
    - Async event handling
    - Event history
    - Type-safe events
    """
    
    def __init__(self, max_history: int = 1000):
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: List[Event] = []
        self._max_history = max_history
        self._lock = asyncio.Lock()
    
    async def publish(self, event: Event) -> None:
        """
        Publish event to all subscribers
        
        Args:
            event: Event to publish
        """
        async with self._lock:
            # Add to history
            self._event_history.append(event)
            if len(self._event_history) > self._max_history:
                self._event_history.pop(0)
        
        # Notify subscribers
        subscribers = self._subscribers.get(event.event_type, [])
        await asyncio.gather(*[
            self._call_handler(handler, event)
            for handler in subscribers
        ])
    
    async def subscribe(
        self, event_type: str, handler: Callable[[Event], None]
    ) -> str:
        """
        Subscribe to event type
        
        Args:
            event_type: Type of event to subscribe to
            handler: Async callback function
            
        Returns:
            Subscription ID
        """
        async with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            
            self._subscribers[event_type].append(handler)
            subscription_id = f"{event_type}_{len(self._subscribers[event_type])}"
        
        return subscription_id
    
    async def unsubscribe(self, event_type: str, handler: Callable) -> bool:
        """
        Unsubscribe from event type
        
        Args:
            event_type: Type of event
            handler: Handler to remove
            
        Returns:
            True if unsubscribed, False if not found
        """
        async with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(handler)
                    return True
                except ValueError:
                    pass
        return False
    
    async def get_history(
        self, event_type: Optional[str] = None, limit: int = 100
    ) -> List[Event]:
        """
        Get event history
        
        Args:
            event_type: Optional filter by type
            limit: Maximum events to return
            
        Returns:
            List of events
        """
        if event_type:
            events = [e for e in self._event_history if e.event_type == event_type]
        else:
            events = self._event_history
        
        return events[-limit:]
    
    async def _call_handler(self, handler: Callable, event: Event) -> None:
        """Call event handler with error handling"""
        try:
            if asyncio.iscoroutinefunction(handler):
                await handler(event)
            else:
                handler(event)
        except Exception as e:
            logger.error(f"Error in event handler: {e}")
```

## Data Models

### Complete Pydantic Models

```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum
from pathlib import Path

# Enums
class RepoType(str, Enum):
    FRONTEND = "frontend"
    BACKEND = "backend"
    FULLSTACK = "fullstack"
    EMPTY = "empty"

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class EventType(str, Enum):
    API_UPDATE = "api_update"
    SCHEMA_CHANGE = "schema_change"
    TASK_COMPLETE = "task_complete"
    DEPENDENCY_NOTIFY = "dependency_notify"

# Models
class FileInfo(BaseModel):
    path: str
    size: int
    extension: str
    is_code: bool
    last_modified: Optional[datetime] = None

class RepoMetadata(BaseModel):
    repo_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: RepoType
    path: Path
    remote_url: Optional[str] = None
    branch: str = "main"
    files: List[FileInfo] = []
    summary: str = ""
    dependencies: List[str] = []
    tech_stack: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat()
        }

class Task(BaseModel):
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    repo_id: str
    agent_type: str
    description: str
    dependencies: List[str] = []
    status: TaskStatus = TaskStatus.PENDING
    context: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

class TaskResult(BaseModel):
    task_id: str
    agent_id: str
    status: str
    output: Any
    context_updates: Dict[str, Any] = {}
    errors: List[str] = []
    completed_at: datetime = Field(default_factory=datetime.utcnow)

class Event(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: EventType
    source: str
    target: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any]

# API Request/Response Models
class RegisterRepoRequest(BaseModel):
    remote_url: Optional[str] = None
    local_path: Optional[str] = None
    dest_path: Optional[str] = None
    branch: str = "main"
    
    @validator("dest_path")
    def validate_paths(cls, v, values):
        if not values.get("remote_url") and not values.get("local_path"):
            raise ValueError("Either remote_url or local_path must be provided")
        return v

class OrchestrationRequest(BaseModel):
    repo_ids: List[str]
    task_description: str
    options: Dict[str, Any] = {}

class OrchestrationResult(BaseModel):
    orchestration_id: str
    status: str
    repos: List[str]
    tasks: List[Task]
    started_at: datetime
    completed_at: Optional[datetime] = None
```

## Configuration Management

```python
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    
    # OpenAI Settings
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_temperature: float = 0.7
    
    # Storage Settings
    storage_type: str = "memory"  # "memory" or "chromadb"
    chromadb_persist_dir: str = "./chroma_db"
    
    # Repository Settings
    repos_base_dir: str = "./repos"
    max_repo_size_mb: int = 500
    
    # Orchestration Settings
    max_parallel_agents: int = 5
    max_iterations: int = 10
    task_timeout_seconds: int = 300
    
    # Logging Settings
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    use_rich_logging: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Global settings instance
settings = Settings()
```

## Performance Considerations

### Async Operations
- All I/O operations are async
- Use `asyncio.gather()` for parallel execution
- Implement connection pooling for external services

### Memory Management
- Limit in-memory context store size
- Implement LRU cache for frequently accessed data
- Stream large files instead of loading entirely

### Scalability
- Stateless agent design
- Horizontal scaling ready
- Event-driven architecture

## Security Considerations

### API Security
- Input validation with Pydantic
- Rate limiting (future)
- API key authentication (future)

### Repository Access
- Validate repository paths
- Sandbox git operations
- Limit repository size

### LLM Security
- Sanitize prompts
- Limit token usage
- Timeout protection

---

**Version**: 1.0  
**Last Updated**: 2026-05-16  
**Status**: Ready for Implementation