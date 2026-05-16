# RepoMesh AI - Workflow Guide

## Overview

This guide provides detailed visualizations and explanations of how RepoMesh AI orchestrates multi-agent workflows across repositories.

## Complete System Workflow

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Orchestrator
    participant Planner
    participant Distributor
    participant FrontendAgent
    participant BackendAgent
    participant Context
    participant EventBus
    participant RepoManager

    User->>API: POST /api/v1/repos/register
    API->>RepoManager: Register repositories
    RepoManager->>RepoManager: Clone/Load repos
    RepoManager->>RepoManager: Index files
    RepoManager-->>API: Return metadata
    API-->>User: Repository registered

    User->>API: POST /api/v1/orchestrate
    API->>Orchestrator: Start workflow
    
    Orchestrator->>Planner: Analyze repos
    Planner->>RepoManager: Get repo metadata
    RepoManager-->>Planner: Metadata
    Planner->>Planner: Create task plan
    Planner-->>Orchestrator: Tasks + Dependencies
    
    Orchestrator->>Distributor: Distribute tasks
    Distributor->>Distributor: Group by agent type
    
    par Parallel Execution
        Distributor->>FrontendAgent: Frontend tasks
        FrontendAgent->>RepoManager: Get repo files
        FrontendAgent->>Context: Get API contracts
        FrontendAgent->>FrontendAgent: Analyze components
        FrontendAgent->>Context: Store UI patterns
        FrontendAgent->>EventBus: Publish completion
        
        Distributor->>BackendAgent: Backend tasks
        BackendAgent->>RepoManager: Get repo files
        BackendAgent->>BackendAgent: Extract endpoints
        BackendAgent->>Context: Store API contracts
        BackendAgent->>EventBus: Publish schema changes
    end
    
    Orchestrator->>Orchestrator: Context Sync
    Orchestrator->>Context: Consolidate updates
    Context->>EventBus: Notify all agents
    
    Orchestrator-->>API: Workflow complete
    API-->>User: Results
```

## Detailed Component Workflows

### 1. Repository Registration Flow

```mermaid
flowchart TD
    Start([User Registers Repo]) --> CheckType{Remote or Local?}
    
    CheckType -->|Remote URL| Clone[Clone Repository]
    CheckType -->|Local Path| Load[Load Local Repo]
    
    Clone --> Validate[Validate Repository]
    Load --> Validate
    
    Validate --> Scan[Scan File Structure]
    Scan --> Detect[Detect Tech Stack]
    Detect --> Index[Index Code Files]
    Index --> Summary[Generate Summary]
    Summary --> Store[Store Metadata]
    Store --> End([Return RepoMetadata])
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style Clone fill:#fff9c4
    style Load fill:#fff9c4
```

**Steps Explained**:

1. **Input Validation**: Check if remote URL or local path provided
2. **Repository Access**: Clone from Git or load from filesystem
3. **Validation**: Verify repository structure and accessibility
4. **File Scanning**: Recursively scan all files and directories
5. **Tech Stack Detection**: Identify languages and frameworks
6. **Code Indexing**: Extract code files and prepare for analysis
7. **Summary Generation**: Create lightweight repository summary
8. **Metadata Storage**: Store all information for future access

### 2. Orchestration Workflow

```mermaid
flowchart TD
    Start([Orchestration Triggered]) --> Init[Initialize State]
    Init --> Planner[Planner Node]
    
    Planner --> Analyze[Analyze Repositories]
    Analyze --> CreateTasks[Create Task List]
    CreateTasks --> MapDeps[Map Dependencies]
    MapDeps --> Distributor[Task Distributor]
    
    Distributor --> Group{Group Tasks}
    Group -->|Frontend| FE[Frontend Agent Node]
    Group -->|Backend| BE[Backend Agent Node]
    
    FE --> FEProcess[Process Frontend Tasks]
    BE --> BEProcess[Process Backend Tasks]
    
    FEProcess --> FEContext[Update Context]
    BEProcess --> BEContext[Update Context]
    
    FEContext --> Sync[Context Sync Node]
    BEContext --> Sync
    
    Sync --> Consolidate[Consolidate Updates]
    Consolidate --> Notify[Notify Agents]
    Notify --> End([Workflow Complete])
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style Planner fill:#fff9c4
    style Distributor fill:#fff9c4
    style Sync fill:#fff9c4
```

**Node Responsibilities**:

#### Planner Node
- Analyzes all registered repositories
- Identifies cross-repository dependencies
- Creates prioritized task list
- Assigns tasks to appropriate agents

#### Task Distributor Node
- Groups tasks by agent type
- Checks task dependencies
- Enables parallel execution
- Routes to agent nodes

#### Agent Nodes (Frontend/Backend)
- Process assigned tasks
- Access shared context
- Analyze repository code
- Generate insights
- Publish updates

#### Context Sync Node
- Collects all context updates
- Resolves conflicts
- Updates shared memory
- Notifies all agents

### 3. Agent Task Processing

```mermaid
flowchart TD
    Start([Receive Task]) --> GetContext[Get Relevant Context]
    GetContext --> GetRepo[Get Repository Files]
    GetRepo --> Analyze{Agent Type?}
    
    Analyze -->|Frontend| FEAnalyze[Analyze Components]
    Analyze -->|Backend| BEAnalyze[Analyze Endpoints]
    
    FEAnalyze --> FEExtract[Extract UI Patterns]
    BEAnalyze --> BEExtract[Extract API Contracts]
    
    FEExtract --> FELLM[Call LLM for Insights]
    BEExtract --> BELLM[Call LLM for Insights]
    
    FELLM --> FEStore[Store UI Patterns]
    BELLM --> BEStore[Store API Contracts]
    
    FEStore --> Publish[Publish Events]
    BEStore --> Publish
    
    Publish --> Result[Create Task Result]
    Result --> End([Return Result])
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style FELLM fill:#ffccbc
    style BELLM fill:#ffccbc
```

### 4. Shared Context Flow

```mermaid
flowchart LR
    subgraph Agents
        FE[Frontend Agent]
        BE[Backend Agent]
    end
    
    subgraph Context Manager
        Store[Context Store]
        Search[Search Engine]
    end
    
    subgraph Storage
        Memory[In-Memory]
        Chroma[ChromaDB]
    end
    
    FE -->|Store UI Patterns| Store
    BE -->|Store API Contracts| Store
    
    Store --> Memory
    Store --> Chroma
    
    FE -->|Query Context| Search
    BE -->|Query Context| Search
    
    Search --> Memory
    Search --> Chroma
    
    Memory -->|Results| Search
    Chroma -->|Results| Search
    
    Search -->|Relevant Context| FE
    Search -->|Relevant Context| BE
    
    style Store fill:#fff9c4
    style Search fill:#fff9c4
```

### 5. Event System Flow

```mermaid
sequenceDiagram
    participant BE as Backend Agent
    participant EB as Event Bus
    participant FE as Frontend Agent
    participant Context as Context Manager

    Note over BE,FE: Agent subscribes to events
    FE->>EB: Subscribe to SCHEMA_CHANGE
    FE->>EB: Subscribe to API_UPDATE
    
    Note over BE,FE: Backend agent detects change
    BE->>BE: Analyze database schema
    BE->>Context: Store schema changes
    BE->>EB: Publish SCHEMA_CHANGE event
    
    Note over BE,FE: Event propagation
    EB->>FE: Notify SCHEMA_CHANGE
    FE->>Context: Query updated schema
    Context-->>FE: Schema details
    FE->>FE: Update frontend models
    
    Note over BE,FE: API contract update
    BE->>Context: Store API contract
    BE->>EB: Publish API_UPDATE event
    EB->>FE: Notify API_UPDATE
    FE->>Context: Query API contract
    Context-->>FE: Contract details
    FE->>FE: Update API integration
```

## State Management

### Orchestration State Structure

```mermaid
classDiagram
    class OrchestrationState {
        +List~RepoMetadata~ repos
        +List~Task~ tasks
        +Dict task_results
        +Dict dependencies
        +Dict shared_context
        +List~Event~ events
        +str status
        +str current_step
        +int iteration
        +datetime started_at
        +datetime completed_at
    }
    
    class RepoMetadata {
        +str repo_id
        +str name
        +RepoType type
        +Path path
        +List~FileInfo~ files
        +str summary
        +List~str~ tech_stack
    }
    
    class Task {
        +str task_id
        +str repo_id
        +str agent_type
        +str description
        +List~str~ dependencies
        +TaskStatus status
        +Dict context
    }
    
    class Event {
        +str event_id
        +EventType event_type
        +str source
        +datetime timestamp
        +Dict payload
    }
    
    OrchestrationState --> RepoMetadata
    OrchestrationState --> Task
    OrchestrationState --> Event
```

## Execution Examples

### Example 1: Single Frontend Repository

```mermaid
gantt
    title Frontend Repository Analysis
    dateFormat  HH:mm:ss
    axisFormat %H:%M:%S
    
    section Registration
    Register Repo           :done, reg, 00:00:00, 5s
    Index Files            :done, idx, after reg, 3s
    
    section Orchestration
    Initialize             :done, init, after idx, 1s
    Planner Node          :done, plan, after init, 2s
    Task Distributor      :done, dist, after plan, 1s
    
    section Agent Execution
    Frontend Agent        :active, fe, after dist, 10s
    Analyze Components    :active, comp, after dist, 4s
    Check API Integration :active, api, after comp, 3s
    Generate Insights     :active, ins, after api, 3s
    
    section Finalization
    Context Sync          :sync, after fe, 2s
    Complete              :crit, done, after sync, 1s
```

### Example 2: Frontend + Backend Coordination

```mermaid
gantt
    title Multi-Repository Orchestration
    dateFormat  HH:mm:ss
    axisFormat %H:%M:%S
    
    section Registration
    Register Frontend      :done, fe-reg, 00:00:00, 5s
    Register Backend       :done, be-reg, 00:00:00, 5s
    
    section Orchestration
    Initialize            :done, init, after be-reg, 1s
    Planner Node         :done, plan, after init, 3s
    Task Distributor     :done, dist, after plan, 1s
    
    section Parallel Execution
    Frontend Agent       :active, fe, after dist, 10s
    Backend Agent        :active, be, after dist, 12s
    
    section Context Sharing
    BE Publishes API     :crit, api, 00:00:15, 1s
    FE Receives API      :crit, recv, after api, 1s
    FE Updates Code      :active, upd, after recv, 3s
    
    section Finalization
    Context Sync         :sync, after be, 2s
    Complete             :crit, done, after sync, 1s
```

## Error Handling Flow

```mermaid
flowchart TD
    Start([Task Execution]) --> Try{Try Execute}
    
    Try -->|Success| Success[Task Complete]
    Try -->|Error| Catch[Catch Exception]
    
    Catch --> Log[Log Error]
    Log --> Retry{Retry?}
    
    Retry -->|Yes| Backoff[Exponential Backoff]
    Retry -->|No| Fail[Mark Failed]
    
    Backoff --> Try
    
    Fail --> Event[Publish Error Event]
    Event --> Notify[Notify Other Agents]
    Notify --> Cleanup[Cleanup Resources]
    
    Success --> Result[Return Result]
    Cleanup --> Result
    Result --> End([End])
    
    style Start fill:#e1f5ff
    style End fill:#c8e6c9
    style Catch fill:#ffcdd2
    style Fail fill:#ffcdd2
```

## Performance Optimization

### Parallel Execution Strategy

```mermaid
flowchart LR
    subgraph Sequential
        S1[Task 1] --> S2[Task 2]
        S2 --> S3[Task 3]
        S3 --> S4[Task 4]
    end
    
    subgraph Parallel
        P1[Task 1]
        P2[Task 2]
        P3[Task 3]
        P4[Task 4]
    end
    
    Sequential -.->|Slow| Time1[40s total]
    Parallel -.->|Fast| Time2[10s total]
    
    style Sequential fill:#ffcdd2
    style Parallel fill:#c8e6c9
```

**Benefits**:
- 4x faster execution with 4 parallel tasks
- Better resource utilization
- Reduced total orchestration time

### Caching Strategy

```mermaid
flowchart TD
    Request[Agent Request] --> Cache{In Cache?}
    
    Cache -->|Yes| Return[Return Cached]
    Cache -->|No| Fetch[Fetch from Store]
    
    Fetch --> Process[Process Data]
    Process --> Store[Store in Cache]
    Store --> Return
    
    Return --> End([Response])
    
    style Cache fill:#fff9c4
    style Return fill:#c8e6c9
```

## Monitoring and Observability

### Execution Trace Example

```
[2026-05-16 03:20:00] [orchestrator] Starting orchestration workflow
[2026-05-16 03:20:01] [planner] Analyzing 2 repositories
[2026-05-16 03:20:02] [planner] Created 4 tasks with 2 dependencies
[2026-05-16 03:20:03] [distributor] Distributing tasks to agents
[2026-05-16 03:20:03] [frontend-agent] Processing task: analyze_frontend_repo
[2026-05-16 03:20:03] [backend-agent] Processing task: analyze_backend_repo
[2026-05-16 03:20:08] [backend-agent] Extracted 15 API endpoints
[2026-05-16 03:20:09] [backend-agent] Published API_UPDATE event
[2026-05-16 03:20:10] [frontend-agent] Received API_UPDATE event
[2026-05-16 03:20:12] [frontend-agent] Updated API integration
[2026-05-16 03:20:13] [context-sync] Synchronizing shared context
[2026-05-16 03:20:14] [orchestrator] Workflow completed successfully
```

## Best Practices

### 1. Task Design
- Keep tasks focused and single-purpose
- Define clear dependencies
- Enable parallel execution where possible
- Include timeout limits

### 2. Context Management
- Store only essential information
- Use descriptive keys
- Include metadata for filtering
- Clean up stale context

### 3. Event Handling
- Subscribe only to relevant events
- Handle events asynchronously
- Include error handling
- Log all event activity

### 4. Agent Implementation
- Implement idempotent operations
- Use structured logging
- Handle partial failures gracefully
- Publish progress updates

## Troubleshooting Guide

### Common Issues

**Issue**: Orchestration hangs
- **Cause**: Circular dependencies
- **Solution**: Review task dependencies, ensure DAG structure

**Issue**: Context not shared
- **Cause**: Event not published
- **Solution**: Verify event publishing in agent code

**Issue**: Agent timeout
- **Cause**: LLM call too slow
- **Solution**: Increase timeout or optimize prompt

**Issue**: Memory usage high
- **Cause**: Large context store
- **Solution**: Implement cleanup policy, use ChromaDB

---

**Version**: 1.0  
**Last Updated**: 2026-05-16  
**Status**: Complete