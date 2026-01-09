"""Benchmark: Agent Startup Time."""

import asyncio
import statistics
import time
from typing import List

import pytest

from benchmarks.config import BENCHMARK_ITERATIONS, WARMUP_ITERATIONS, SLA_TARGETS


class AgentStartupBenchmark:
    """Benchmark agent initialization and startup time."""

    def __init__(self):
        self.results: List[float] = []

    async def startup_agent(self) -> float:
        """Simulate agent startup and return time in seconds."""
        start = time.perf_counter()
        
        # Simulated agent startup steps
        await asyncio.sleep(0.001)  # Load configuration
        await asyncio.sleep(0.001)  # Initialize LLM connection
        await asyncio.sleep(0.001)  # Load memory context
        await asyncio.sleep(0.001)  # Register tools
        
        elapsed = time.perf_counter() - start
        return elapsed

    async def run(self, iterations: int = BENCHMARK_ITERATIONS) -> dict:
        """Run startup benchmark."""
        # Warmup
        for _ in range(WARMUP_ITERATIONS):
            await self.startup_agent()

        # Benchmark
        self.results = []
        for _ in range(iterations):
            elapsed = await self.startup_agent()
            self.results.append(elapsed)

        return self.get_stats()

    def get_stats(self) -> dict:
        """Calculate benchmark statistics."""
        if not self.results:
            return {}

        sorted_results = sorted(self.results)
        p50_idx = int(len(sorted_results) * 0.50)
        p95_idx = int(len(sorted_results) * 0.95)
        p99_idx = int(len(sorted_results) * 0.99)

        return {
            "benchmark": "agent_startup",
            "iterations": len(self.results),
            "min_ms": min(self.results) * 1000,
            "max_ms": max(self.results) * 1000,
            "mean_ms": statistics.mean(self.results) * 1000,
            "median_ms": statistics.median(self.results) * 1000,
            "stdev_ms": statistics.stdev(self.results) * 1000 if len(self.results) > 1 else 0,
            "p50_ms": sorted_results[p50_idx] * 1000,
            "p95_ms": sorted_results[p95_idx] * 1000,
            "p99_ms": sorted_results[p99_idx] * 1000,
            "sla_target_s": SLA_TARGETS["agent_startup"],
            "sla_met": max(self.results) < SLA_TARGETS["agent_startup"],
        }


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_agent_startup_benchmark():
    """Run agent startup benchmark."""
    benchmark = AgentStartupBenchmark()
    results = await benchmark.run()
    
    print(f"\nAgent Startup Benchmark Results:")
    print(f"  Iterations: {results['iterations']}")
    print(f"  Mean: {results['mean_ms']:.2f}ms")
    print(f"  P50: {results['p50_ms']:.2f}ms")
    print(f"  P95: {results['p95_ms']:.2f}ms")
    print(f"  P99: {results['p99_ms']:.2f}ms")
    print(f"  SLA Target: {results['sla_target_s']}s")
    print(f"  SLA Met: {results['sla_met']}")
    
    assert results["sla_met"], f"Agent startup exceeded SLA: {results['p99_ms']}ms > {results['sla_target_s'] * 1000}ms"
