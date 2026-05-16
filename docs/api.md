# RepoMesh AI - API Documentation

## Overview

RepoMesh AI provides a RESTful API for managing repositories, running orchestration workflows, and accessing shared context. All endpoints return JSON responses and support standard HTTP methods.

**Base URL**: `http://localhost:8000`  
**API Version**: v1  
**API Prefix**: `/api/v1`

---

## Authentication

Currently, the API does not require authentication. Future versions will support API key authentication.

---

## Health Check

### GET /health

Check the health status of the API.

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "service": "RepoMesh AI"
}
```

---

## Repository Management

### POST /api/v1/repos/register

Register a new repository for analysis.

**Request Body**:
```json
{
  "url": "https://github.com/user/repo.git",  // Optional: Git URL
  "path": "/path/to/local/repo",              // Optional: Local path
  "name": "my-repo"                            // Optional: Custom name
}
```

**Note**: Either `url` or `path` must be provided.

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "my-repo",
  "path": "/path/to/repo",
  "url": "https://github.com/user/repo.git",
  "repo_type": "fullstack",
  "tech_stack": ["React", "FastAPI", "PostgreSQL"],
  "file_count": 150,
  "code_file_count": 85,
  "total_lines": 12500,
  "summary": "Repository: my-repo\nType: fullstack\n..."
}
```

**Error Responses**:
- `400 Bad Request`: Invalid request (missing url/path)
- `500 Internal Server Error`: Repository operation failed

---

### GET /api/v1/repos

List all registered repositories.

**Response** (200 OK):
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "frontend-app",
    "path": "/repos/frontend-app",
    "url": null,
    "repo_type": "frontend",
    "tech_stack": ["React", "TypeScript"],
    "file_count": 75,
    "code_file_count": 45,
    "total_lines": 5000,
    "summary": "..."
  }
]
```

---

### GET /api/v1/repos/{repo_id}

Get details for a specific repository.

**Path Parameters**:
- `repo_id` (UUID): Repository ID

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "backend-api",
  "path": "/repos/backend-api",
  "url": "https://github.com/user/backend-api.git",
  "repo_type": "backend",
  "tech_stack": ["FastAPI", "PostgreSQL"],
  "file_count": 100,
  "code_file_count": 60,
  "total_lines": 8000,
  "summary": "..."
}
```

**Error Responses**:
- `404 Not Found`: Repository not found

---

### DELETE /api/v1/repos/{repo_id}

Delete a repository from the system.

**Path Parameters**:
- `repo_id` (UUID): Repository ID

**Query Parameters**:
- `delete_files` (boolean, optional): Whether to delete repository files (default: false)

**Response** (200 OK):
```json
{
  "message": "Repository deleted successfully"
}
```

**Error Responses**:
- `404 Not Found`: Repository not found

---

## Orchestration

### POST /api/v1/orchestrate

Start an orchestration workflow to analyze repositories.

**Request Body**:
```json
{
  "repo_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ]
}
```

**Response** (200 OK):
```json
{
  "repo_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660e8400-e29b-41d4-a716-446655440001"
  ],
  "total_tasks": 4,
  "completed_tasks": 4,
  "failed_tasks": 0,
  "execution_time_seconds": 12.5,
  "results": {
    "task-id-1": {
      "components": [...],
      "ui_patterns": [...],
      "summary": "..."
    },
    "task-id-2": {
      "endpoints": [...],
      "schemas": [...],
      "summary": "..."
    }
  }
}
```

**Error Responses**:
- `400 Bad Request`: Invalid UUID format
- `500 Internal Server Error`: Orchestration failed

---

## Context Management

### POST /api/v1/context/search

Search for context entries.

**Request Body**:
```json
{
  "query": "API endpoints",
  "repo_id": "550e8400-e29b-41d4-a716-446655440000",  // Optional
  "top_k": 10                                          // Optional (default: 10)
}
```

**Response** (200 OK):
```json
{
  "query": "API endpoints",
  "results": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440000",
      "key": "api_contract:550e8400:backend_api",
      "content": "Found 15 API endpoints...",
      "metadata": {
        "type": "api_contract",
        "count": 15
      },
      "repo_id": "550e8400-e29b-41d4-a716-446655440000",
      "agent_type": "backend",
      "created_at": "2026-05-16T09:00:00Z"
    }
  ],
  "count": 1
}
```

**Error Responses**:
- `400 Bad Request`: Invalid UUID format
- `500 Internal Server Error`: Search failed

---

### GET /api/v1/context/keys

List all context keys.

**Query Parameters**:
- `repo_id` (UUID, optional): Filter by repository ID

**Response** (200 OK):
```json
[
  "architecture:550e8400:frontend",
  "api_contract:550e8400:backend_api",
  "component:550e8400:UserProfile"
]
```

---

### GET /api/v1/context/{key}

Get a specific context entry by key.

**Path Parameters**:
- `key` (string): Context key

**Response** (200 OK):
```json
{
  "id": "770e8400-e29b-41d4-a716-446655440000",
  "key": "api_contract:550e8400:backend_api",
  "content": "API contract details...",
  "metadata": {
    "type": "api_contract"
  },
  "repo_id": "550e8400-e29b-41d4-a716-446655440000",
  "agent_type": "backend",
  "created_at": "2026-05-16T09:00:00Z"
}
```

**Error Responses**:
- `404 Not Found`: Context not found

---

### DELETE /api/v1/context/{key}

Delete a context entry.

**Path Parameters**:
- `key` (string): Context key

**Response** (200 OK):
```json
{
  "message": "Context deleted successfully"
}
```

**Error Responses**:
- `404 Not Found`: Context not found

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Rate Limiting

Currently, there are no rate limits. Future versions will implement rate limiting.

---

## Examples

### Complete Workflow Example

```bash
# 1. Register a repository
REPO_ID=$(curl -X POST http://localhost:8000/api/v1/repos/register \
  -H "Content-Type: application/json" \
  -d '{"path": "/path/to/repo"}' | jq -r '.id')

# 2. Run orchestration
curl -X POST http://localhost:8000/api/v1/orchestrate \
  -H "Content-Type: application/json" \
  -d "{\"repo_ids\": [\"$REPO_ID\"]}"

# 3. Search context
curl -X POST http://localhost:8000/api/v1/context/search \
  -H "Content-Type: application/json" \
  -d '{"query": "components", "repo_id": "'$REPO_ID'"}'

# 4. List all context keys
curl http://localhost:8000/api/v1/context/keys?repo_id=$REPO_ID
```

---

## Interactive Documentation

Visit these URLs for interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These interfaces allow you to:
- Explore all endpoints
- View request/response schemas
- Test API calls directly from the browser
- Download OpenAPI specification

---

## SDK Support

Currently, the API can be accessed using any HTTP client. Future versions will provide official SDKs for:
- Python
- JavaScript/TypeScript
- Go

---

## Changelog

### v0.1.0 (2026-05-16)
- Initial API release
- Repository management endpoints
- Orchestration workflow endpoint
- Context management endpoints
- Health check endpoint