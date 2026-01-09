#!/bin/bash
# Agile-PM API cURL Examples

BASE_URL="http://localhost:8000/api/v1"
TOKEN="your-jwt-token"

# Health Check (no auth required)
echo "=== Health Check ==="
curl -s "$BASE_URL/system/health" | jq

# List Agents
echo "=== List Agents ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/agents" | jq

# Create Agent
echo "=== Create Agent ==="
curl -s -X POST "$BASE_URL/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Agent", "type": "backend"}' | jq

# Get Agent
echo "=== Get Agent ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/agents/agent-001" | jq

# Create Task
echo "=== Create Task ==="
curl -s -X POST "$BASE_URL/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Task", "priority": "P0"}' | jq

# List Tasks
echo "=== List Tasks ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/tasks" | jq

# System Metrics
echo "=== System Metrics ==="
curl -s -H "Authorization: Bearer $TOKEN" "$BASE_URL/system/metrics" | jq
