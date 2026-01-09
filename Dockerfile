# Agile-PM Docker Image
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY pyproject.toml README.md ./
COPY src/ ./src/

RUN pip install --no-cache-dir -e ".[full]"

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/system/health || exit 1

# Run server
CMD ["agile-pm", "serve", "--host", "0.0.0.0", "--port", "8000"]
