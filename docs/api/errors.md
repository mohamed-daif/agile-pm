# Error Handling

## Error Response Format

All errors return JSON with this structure:

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE",
  "path": "/api/v1/resource"
}
```

## HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Missing/invalid auth |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Too Many Requests - Rate limited |
| 500 | Internal Server Error |

## Common Errors

### Authentication Required

```json
{
  "detail": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

### Insufficient Permissions

```json
{
  "detail": "Insufficient permissions",
  "code": "FORBIDDEN"
}
```

### Rate Limit Exceeded

```json
{
  "detail": "Rate limit exceeded",
  "code": "RATE_LIMITED"
}
```

Headers: `Retry-After: 60`

### Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```
