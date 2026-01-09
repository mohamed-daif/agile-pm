# Agile-PM Monitoring Guide

## Overview

Agile-PM uses a comprehensive observability stack:
- **Metrics**: Prometheus + Grafana
- **Tracing**: OpenTelemetry + Jaeger
- **Logging**: Structured JSON logs + Loki

## Dashboards

### Main Dashboard (`agile-pm-overview`)

Import from `monitoring/grafana/agile-pm-dashboard.json`.

Key panels:
- Request Rate & Latency
- Error Rate
- Queue Depth
- Agent Activity
- Database Connections

## Alerts

Alert rules are defined in `monitoring/prometheus/alert-rules.yml`.

### Critical Alerts

| Alert | Condition | Response |
|-------|-----------|----------|
| HighErrorRate | >5% 5xx errors for 5m | Check logs, rollback if needed |
| DatabaseConnectionsExhausted | >90% pool used | Scale connections or instances |
| ServiceDown | Service unreachable 1m | Check pods, restart if needed |
| RedisConnectionFailed | Redis unreachable | Check Redis pod/service |

### Warning Alerts

| Alert | Condition | Response |
|-------|-----------|----------|
| HighLatency | p95 > 1s for 5m | Profile endpoints, check queries |
| QueueBacklog | >100 tasks for 10m | Scale workers |
| HighMemoryUsage | >85% limit | Check for leaks, increase limit |
| WebhookDeliveryFailures | >10% failing | Check webhook endpoints |

## Runbook

### High Error Rate

1. Check recent deployments: `kubectl rollout history deployment/agile-pm-api`
2. Review error logs: `kubectl logs -l app=agile-pm-api --tail=100 | jq 'select(.level=="error")'`
3. Check database connectivity
4. If recent deploy, rollback: `kubectl rollout undo deployment/agile-pm-api`

### Database Connection Exhaustion

1. Check current connections: `SELECT count(*) FROM pg_stat_activity WHERE application_name = 'agile-pm';`
2. Identify long-running queries: `SELECT * FROM pg_stat_activity WHERE state = 'active' ORDER BY query_start;`
3. Kill idle connections if needed
4. Consider increasing pool size

### Queue Backlog

1. Check worker status: `celery -A agile_pm.queue.celery_app inspect active`
2. Review failed tasks: `celery -A agile_pm.queue.celery_app inspect reserved`
3. Scale workers: `kubectl scale deployment/agile-pm-worker --replicas=5`
4. Check for stuck tasks

## SLO Definitions

| SLI | Target | Measurement |
|-----|--------|-------------|
| Availability | 99.9% | `up{job="agile-pm"}` |
| Latency p95 | < 500ms | `histogram_quantile(0.95, ...)` |
| Error Rate | < 0.1% | `rate(http_requests_total{status=~"5.."}[5m])` |
| Webhook Delivery | 99% | `webhook_deliveries_total{status="success"}` |

## Troubleshooting

### Enable Debug Logging
```bash
kubectl set env deployment/agile-pm-api LOG_LEVEL=DEBUG
```

### Enable Profiling
```bash
curl -X POST http://localhost:8000/debug/profiling/enable
```

### Get Slow Queries
```bash
curl http://localhost:8000/debug/slow-queries
```
