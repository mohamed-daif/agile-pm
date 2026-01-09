# Sprints API

## List Sprints

```http
GET /api/v1/sprints
```

## Create Sprint

```http
POST /api/v1/sprints
```

### Request Body

```json
{
  "name": "Sprint 01",
  "goal": "Implement core features",
  "start_date": "2026-01-10",
  "end_date": "2026-01-17",
  "points": 40
}
```

## Get Sprint

```http
GET /api/v1/sprints/{sprint_id}
```

## Update Sprint

```http
PUT /api/v1/sprints/{sprint_id}
```
