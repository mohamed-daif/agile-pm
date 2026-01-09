# API Authentication

## Overview

Agile-PM API supports two authentication methods:

1. **JWT Tokens** - For user sessions and interactive access
2. **API Keys** - For service accounts and automation

## JWT Authentication

### Obtaining a Token

```python
from agile_pm.api.auth.jwt import JWTHandler

handler = JWTHandler(secret="your-secret-key")
token = handler.create_token(
    user_id="user-123",
    roles=["operator"]
)
```

### Using the Token

```bash
curl -H "Authorization: Bearer eyJ..." http://localhost:8000/api/v1/agents
```

### Token Refresh

Tokens expire after 30 minutes by default. Refresh before expiry:

```python
new_token = handler.refresh_token(old_token)
```

## API Key Authentication

### Creating an API Key

```python
from agile_pm.api.auth.api_keys import APIKeyManager

manager = APIKeyManager()
key, api_key_obj = manager.create_key(
    name="my-service",
    roles=["viewer"]
)
# Store `key` securely - it's only shown once!
```

### Using the API Key

```bash
curl -H "X-API-Key: <key>" http://localhost:8000/api/v1/agents
```

## Roles and Permissions

| Role | Permissions |
|------|-------------|
| `admin` | Full access to all resources |
| `operator` | Read, write, execute agents and tasks |
| `viewer` | Read-only access |
| `service` | Execute agents and tasks |

## Security Best Practices

1. **Never expose secrets** in client-side code
2. **Use API keys** for automated systems
3. **Use JWT** for user sessions
4. **Rotate API keys** regularly
5. **Use HTTPS** in production
