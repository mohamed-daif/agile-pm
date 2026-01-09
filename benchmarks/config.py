"""Benchmark Configuration."""

import os

# Benchmark settings
BENCHMARK_ITERATIONS = int(os.getenv("BENCHMARK_ITERATIONS", "100"))
WARMUP_ITERATIONS = int(os.getenv("WARMUP_ITERATIONS", "10"))
TIMEOUT_SECONDS = int(os.getenv("BENCHMARK_TIMEOUT", "300"))

# Target SLAs (in seconds)
SLA_TARGETS = {
    "agent_startup": 2.0,           # Agent should start in < 2s
    "task_planning": 30.0,          # Task planning < 30s
    "memory_read": 0.1,             # Memory read < 100ms
    "memory_write": 0.2,            # Memory write < 200ms
    "crew_execution": 120.0,        # Crew execution < 2min
    "api_response_p95": 0.5,        # API P95 < 500ms
    "api_response_p99": 1.0,        # API P99 < 1s
}

# Output configuration
RESULTS_DIR = os.getenv("RESULTS_DIR", "benchmark-results")
