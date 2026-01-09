# Configuration Guide

Agile-PM can be configured through environment variables, YAML configuration files, or programmatically.

## Configuration File

Create `.agile-pm.yml` in your project root:

```yaml
# Agile-PM Configuration
version: "1.0"

# Agent Configuration
agents:
  max_concurrent: 5           # Maximum concurrent agents
  default_timeout: 300        # Task timeout in seconds
  retry_attempts: 3           # Retry failed tasks
  
  # Agent pool configuration
  pool:
    strategic:
      - name: "Technical PM"
        capabilities: ["planning", "architecture"]
    executor:
      - name: "Backend Engineer"
        capabilities: ["python", "api", "database"]
      - name: "Frontend Engineer"
        capabilities: ["react", "typescript", "ui"]
    reviewer:
      - name: "QA Engineer"
        capabilities: ["testing", "validation"]

# LLM Configuration
llm:
  provider: openai            # openai, anthropic, ollama
  model: gpt-4
  temperature: 0.7
  max_tokens: 4096
  
  # Provider-specific settings
  openai:
    organization: ""
    api_base: ""              # Custom endpoint
  
  anthropic:
    model: claude-3-opus

# Memory Configuration
memory:
  backend: redis              # redis, postgres, memory
  ttl: 86400                  # Cache TTL in seconds
  max_entries: 10000
  
  redis:
    url: "redis://localhost:6379/0"
    prefix: "agilepm:"
  
  postgres:
    url: "postgresql://user:pass@localhost:5432/agilepm"

# Security Configuration
security:
  rate_limit:
    requests_per_minute: 60
    burst: 10
  
  api_key:
    min_length: 32
    max_length: 128
  
  cors:
    allowed_origins:
      - "http://localhost:3000"
      - "http://localhost:3001"
  
  headers:
    x_frame_options: "DENY"
    content_security_policy: "default-src 'self'"

# Resilience Configuration
resilience:
  circuit_breaker:
    failure_threshold: 5
    success_threshold: 3
    timeout: 30
  
  retry:
    max_attempts: 3
    base_delay: 1.0
    max_delay: 60.0
    exponential_base: 2.0

# Logging Configuration
logging:
  level: INFO                 # DEBUG, INFO, WARNING, ERROR
  format: json                # json, text
  output: stdout              # stdout, file
  file_path: "logs/agile-pm.log"
  
  # Sensitive field masking
  mask_fields:
    - password
    - api_key
    - token
    - secret

# Dashboard Configuration
dashboard:
  enabled: true
  host: "0.0.0.0"
  port: 8001
  websocket_port: 8002
  
  # Authentication
  auth:
    enabled: false
    type: basic               # basic, oauth2
    username: admin
    password_hash: ""
```

## Environment Variables

All configuration can be overridden via environment variables:

```bash
# LLM
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-4"
export LLM_TEMPERATURE="0.7"

# Database
export DATABASE_URL="postgresql://user:pass@localhost:5432/agilepm"

# Redis
export REDIS_URL="redis://localhost:6379/0"

# Security
export RATE_LIMIT_RPM="60"
export RATE_LIMIT_BURST="10"

# Logging
export LOG_LEVEL="INFO"
export LOG_FORMAT="json"

# Dashboard
export DASHBOARD_PORT="8001"
```

## Programmatic Configuration

```python
from agile_pm import Config, AgentOrchestrator

# Create config
config = Config(
    agents=AgentsConfig(
        max_concurrent=5,
        default_timeout=300,
    ),
    llm=LLMConfig(
        provider="openai",
        model="gpt-4",
        temperature=0.7,
    ),
    security=SecurityConfig(
        rate_limit_rpm=60,
    ),
)

# Use with orchestrator
orchestrator = AgentOrchestrator(config=config)
```

## Configuration Priority

Configuration is loaded in the following order (later overrides earlier):

1. Default values
2. `.agile-pm.yml` in current directory
3. `~/.agile-pm/config.yml` in home directory
4. Environment variables
5. Programmatic configuration

## Profiles

Use profiles for different environments:

```yaml
# .agile-pm.yml
profiles:
  development:
    logging:
      level: DEBUG
    security:
      rate_limit:
        requests_per_minute: 1000
  
  production:
    logging:
      level: INFO
    security:
      rate_limit:
        requests_per_minute: 60
```

Activate a profile:

```bash
export AGILE_PM_PROFILE=production
# or
agile-pm --profile production execute sprint
```

## Validation

Validate your configuration:

```bash
agile-pm config validate
```

View effective configuration:

```bash
agile-pm config show
```
