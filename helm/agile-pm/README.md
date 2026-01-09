# Agile-PM Helm Chart

## Installation

```bash
# Add the repo (if published)
helm repo add agile-pm https://mohamed-daif.github.io/agile-pm/charts

# Install with default values
helm install agile-pm agile-pm/agile-pm -n agile-pm --create-namespace

# Install with custom values
helm install agile-pm agile-pm/agile-pm -n agile-pm \
  --set ingress.hosts[0].host=myapp.example.com \
  --set secrets.databaseUrl="postgresql://..." \
  --set secrets.redisUrl="redis://..."
```

## Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount.api` | API replicas | `3` |
| `replicaCount.worker` | Worker replicas | `2` |
| `image.repository` | Image repository | `ghcr.io/mohamed-daif/agile-pm` |
| `image.tag` | Image tag | `latest` |
| `ingress.enabled` | Enable ingress | `true` |
| `ingress.hosts[0].host` | Hostname | `agile-pm.example.com` |
| `autoscaling.api.enabled` | Enable HPA for API | `true` |
| `autoscaling.api.maxReplicas` | Max API replicas | `10` |

## External Secrets

For production, use External Secrets Operator:

```yaml
externalSecrets:
  enabled: true
  secretStore: vault-backend
  refreshInterval: 1h
```

## Upgrading

```bash
helm upgrade agile-pm agile-pm/agile-pm -n agile-pm -f values-prod.yaml
```
