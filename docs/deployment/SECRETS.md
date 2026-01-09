# Secrets Management

## Overview

Agile-PM uses External Secrets Operator (ESO) to sync secrets from HashiCorp Vault.

## Setup

### 1. Install External Secrets Operator

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace
```

### 2. Configure Vault

```bash
# Enable Kubernetes auth
vault auth enable kubernetes

# Configure Kubernetes auth
vault write auth/kubernetes/config \
  kubernetes_host="https://$KUBERNETES_SERVICE_HOST:$KUBERNETES_SERVICE_PORT"

# Create policy
vault policy write agile-pm - <<EOF
path "secret/data/agile-pm/*" {
  capabilities = ["read"]
}
EOF

# Create role
vault write auth/kubernetes/role/agile-pm \
  bound_service_account_names=agile-pm \
  bound_service_account_namespaces=agile-pm \
  policies=agile-pm \
  ttl=1h
```

### 3. Store Secrets in Vault

```bash
vault kv put secret/agile-pm/database url="postgresql://user:pass@host:5432/db"
vault kv put secret/agile-pm/redis url="redis://host:6379/0"
vault kv put secret/agile-pm/auth jwt_secret="your-secret" api_key="your-key"
```

## Secret Rotation

Secrets are automatically refreshed every hour (configurable via `refreshInterval`).

For immediate rotation:
1. Update secret in Vault
2. Delete the Kubernetes secret: `kubectl delete secret agile-pm-secrets -n agile-pm`
3. ESO will recreate it with new values

## Environment Separation

| Environment | Vault Path | Namespace |
|-------------|------------|-----------|
| Development | `secret/agile-pm-dev/*` | `agile-pm-dev` |
| Staging | `secret/agile-pm-staging/*` | `agile-pm-staging` |
| Production | `secret/agile-pm/*` | `agile-pm` |
