# Agents API

## List Agents

```http
GET /api/v1/agents
```

### Response

```json
{
  "items": [
    {
      "id": "agent-001",
      "name": "Backend Engineer",
      "type": "backend",
      "status": "active"
    }
  ],
  "total": 1,
  "page": 1,
  "per_page": 20
}
```

## Create Agent

```http
POST /api/v1/agents
```

### Request Body

```json
{
  "name": "New Agent",
  "type": "backend",
  "capabilities": ["code_generation", "testing"]
}
```

### Response

```json
{
  "id": "agent-002",
  "name": "New Agent",
  "type": "backend",
  "status": "active",
  "capabilities": ["code_generation", "testing"]
}
```

## Get Agent

```http
GET /api/v1/agents/{agent_id}
```

## Update Agent

```http
PUT /api/v1/agents/{agent_id}
```

## Delete Agent

```http
DELETE /api/v1/agents/{agent_id}
```

## Execute Agent Task

```http
POST /api/v1/agents/{agent_id}/execute
```

### Request Body

```json
{
  "task": "Implement login feature",
  "context": {
    "language": "python",
    "framework": "fastapi"
  }
}
```

### Response

```json
{
  "execution_id": "exec-001",
  "status": "running",
  "agent_id": "agent-001"
}
```
