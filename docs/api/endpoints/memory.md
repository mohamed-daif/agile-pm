# Memory API

Key-value storage for agent memory.

## List Keys

```http
GET /api/v1/memory
```

## Get Value

```http
GET /api/v1/memory/{key}
```

## Set Value

```http
POST /api/v1/memory/{key}
```

### Request Body

```json
{
  "value": "any JSON value",
  "ttl": 3600
}
```

## Delete Key

```http
DELETE /api/v1/memory/{key}
```
