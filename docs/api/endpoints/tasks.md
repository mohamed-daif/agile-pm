# Tasks API

## List Tasks

```http
GET /api/v1/tasks
```

### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Filter by status |
| `priority` | string | Filter by priority (P0-P3) |
| `sprint_id` | string | Filter by sprint |

## Create Task

```http
POST /api/v1/tasks
```

### Request Body

```json
{
  "title": "Implement authentication",
  "description": "Add JWT auth to API",
  "priority": "P0",
  "sprint_id": "sprint-001"
}
```

## Get Task

```http
GET /api/v1/tasks/{task_id}
```

## Update Task

```http
PUT /api/v1/tasks/{task_id}
```

## Start Task

```http
POST /api/v1/tasks/{task_id}/start
```

## Cancel Task

```http
POST /api/v1/tasks/{task_id}/cancel
```
