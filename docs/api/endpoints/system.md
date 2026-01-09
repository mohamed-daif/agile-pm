# System API

## Health Check

```http
GET /api/v1/system/health
```

**No authentication required**

### Response

```json
{
  "status": "healthy",
  "timestamp": "2026-01-10T12:00:00Z"
}
```

## Metrics

```http
GET /api/v1/system/metrics
```

### Response

```json
{
  "uptime_seconds": 3600,
  "active_agents": 5,
  "pending_tasks": 12,
  "memory_usage_mb": 256
}
```

## System Info

```http
GET /api/v1/system/info
```

### Response

```json
{
  "name": "Agile-PM",
  "version": "1.0.0",
  "python_version": "3.11.0"
}
```
