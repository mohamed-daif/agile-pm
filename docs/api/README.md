# Agile-PM API Reference

> Complete API documentation for Agile-PM REST API

## Overview

The Agile-PM API provides programmatic access to all core functionality:

- **Agents:** Manage AI agents and execute tasks
- **Tasks:** Create, update, and execute tasks
- **Sprints:** Sprint planning and management
- **Memory:** Key-value memory storage
- **System:** Health checks, metrics, and info

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

See [Authentication Guide](./authentication.md) for details.

### JWT Token

```bash
curl -H "Authorization: Bearer <token>" http://localhost:8000/api/v1/agents
```

### API Key

```bash
curl -H "X-API-Key: <api-key>" http://localhost:8000/api/v1/agents
```

## Endpoints

- [Agents](./endpoints/agents.md)
- [Tasks](./endpoints/tasks.md)
- [Sprints](./endpoints/sprints.md)
- [Memory](./endpoints/memory.md)
- [System](./endpoints/system.md)

## Rate Limiting

- **Default:** 60 requests/minute
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## Error Handling

See [Error Handling Guide](./errors.md) for error codes and responses.

## Examples

- [Python Examples](./examples/python/)
- [cURL Examples](./examples/curl/)
