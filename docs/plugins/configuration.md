# Plugin Configuration

## Configuration File

Create `.agile-pm.yml` or `agile-pm.yml`:

```yaml
plugins:
  github:
    enabled: true
    settings:
      token: ${GITHUB_TOKEN}
      repo: owner/repo
  
  jira:
    enabled: true
    settings:
      url: https://company.atlassian.net
      email: ${JIRA_EMAIL}
      api_token: ${JIRA_TOKEN}
      project_key: PROJ
  
  my-plugin:
    enabled: true
    settings:
      api_key: ${MY_PLUGIN_KEY}
```

## Environment Variables

Use `${VAR_NAME}` syntax for secrets.

## Loading Configuration

```python
from agile_pm.plugins.config import PluginsConfig

config = PluginsConfig.from_file(".agile-pm.yml")

if config.is_enabled("github"):
    settings = config.get_plugin_config("github").settings
```
