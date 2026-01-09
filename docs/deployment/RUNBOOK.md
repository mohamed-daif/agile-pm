# Agile-PM Deployment Runbook

## Pre-Deployment Checklist

- [ ] All tests passing in CI
- [ ] Database migrations validated
- [ ] Staging deployment successful
- [ ] Load test baseline met
- [ ] Rollback plan reviewed
- [ ] On-call engineer notified

## Deployment Steps

### 1. Prepare Release

```bash
# Tag the release
git tag -a v1.x.x -m "Release v1.x.x"
git push origin v1.x.x
```

### 2. Deploy to Staging

Automatic via GitHub Actions on tag push.

Verify:
```bash
kubectl get pods -n agile-pm-staging
curl https://staging.agile-pm.example.com/health
```

### 3. Production Deployment

Requires manual approval in GitHub Actions.

1. Go to Actions > Release workflow
2. Review staging metrics
3. Approve production deployment
4. Monitor rollout:

```bash
kubectl rollout status deployment/agile-pm-api -n agile-pm
kubectl get pods -n agile-pm -w
```

### 4. Post-Deployment Verification

```bash
# Health check
curl https://agile-pm.example.com/ready

# Smoke test
curl -H "X-API-Key: $API_KEY" https://agile-pm.example.com/api/v1/agents

# Check metrics
open https://grafana.example.com/d/agile-pm-overview
```

## Rollback Procedure

### Quick Rollback (Helm)

```bash
# List revisions
helm history agile-pm -n agile-pm

# Rollback to previous
helm rollback agile-pm -n agile-pm

# Rollback to specific revision
helm rollback agile-pm 5 -n agile-pm
```

### Kubernetes Rollback

```bash
# Rollback deployment
kubectl rollout undo deployment/agile-pm-api -n agile-pm

# Rollback to specific revision
kubectl rollout undo deployment/agile-pm-api -n agile-pm --to-revision=3
```

### Database Rollback

```bash
# Connect to migration pod
kubectl exec -it deploy/agile-pm-api -n agile-pm -- bash

# Downgrade one revision
alembic downgrade -1

# Or restore from backup
psql $DATABASE_URL < backup-YYYYMMDD-HHMMSS.sql
```

## Incident Response

### High Error Rate

1. Check error logs:
   ```bash
   kubectl logs -l app.kubernetes.io/name=agile-pm -n agile-pm --tail=100 | grep error
   ```

2. Check recent changes:
   ```bash
   helm history agile-pm -n agile-pm
   ```

3. If recent deployment, rollback immediately

4. If not deployment-related, check:
   - Database connectivity
   - Redis connectivity
   - External service status

### Service Degradation

1. Scale up if under load:
   ```bash
   kubectl scale deployment/agile-pm-api -n agile-pm --replicas=10
   ```

2. Check resource usage:
   ```bash
   kubectl top pods -n agile-pm
   ```

3. Check HPA status:
   ```bash
   kubectl describe hpa agile-pm-api -n agile-pm
   ```

## Maintenance Windows

### Database Maintenance

1. Scale down workers:
   ```bash
   kubectl scale deployment/agile-pm-worker -n agile-pm --replicas=0
   ```

2. Run maintenance

3. Scale workers back:
   ```bash
   kubectl scale deployment/agile-pm-worker -n agile-pm --replicas=2
   ```

### Planned Downtime

1. Enable maintenance mode (returns 503):
   ```bash
   kubectl set env deployment/agile-pm-api MAINTENANCE_MODE=true -n agile-pm
   ```

2. Perform maintenance

3. Disable maintenance mode:
   ```bash
   kubectl set env deployment/agile-pm-api MAINTENANCE_MODE=false -n agile-pm
   ```
