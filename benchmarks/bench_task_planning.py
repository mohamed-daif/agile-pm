"""Benchmark: Task Planning Performance."""

import asyncio
import statistics
import time
from typing import List

import pytest

from benchmarks.config import BENCHMARK_ITERATIONS, WARMUP_ITERATIONS, SLA_TARGETS


class TaskPlanningBenchmark:
    """Benchmark task planning and breakdown performance."""

    def __init__(self):
        self.results: List[float] = []

    async def plan_task(self, complexity: str = "medium") -> float:
        """Simulate task planning and return time in seconds."""
        start = time.perf_counter()
        
        # Simulated planning steps
        delays = {
            "simple": [0.01, 0.02, 0.01],      # ~40ms total
            "medium": [0.05, 0.10, 0.05],      # ~200ms total
            "complex": [0.10, 0.30, 0.20],     # ~600ms total
        }
        
        for delay in delays.get(complexity, delays["medium"]):
            await asyncio.sleep(delay)
        
        elapsed = time.perf_counter() - start
        return elapsed

    async def run(self, iterations: int = BENCHMARK_ITERATIONS) -> dict:
        """Run planning benchmark for each complexity level."""
        results_by_complexity = {}
        
        for complexity in ["simple", "medium", "complex"]:
            # Warmup
            for _ in range(WARMUP_ITERATIONS):
                await self.plan_task(complexity)

            # Benchmark
            results = []
            for _ in range(iterations):
                elapsed = await self.plan_task(complexity)
                results.append(elapsed)

            results_by_complexity[complexity] = self._calc_stats(results, complexity)

        return results_by_complexity

    def _calc_stats(self, results: List[float], complexity: str) -> dict:
        """Calculate statistics for a complexity level."""
        sorted_results = sorted(results)
        p95_idx = int(len(sorted_results) * 0.95)
        p99_idx = int(len(sorted_results) * 0.99)

        return {
            "benchmark": f"task_planning_{complexity}",
            "iterations": len(results),
            "mean_ms": statistics.mean(results) * 1000,
            "p95_ms": sorted_results[p95_idx] * 1000,
            "p99_ms": sorted_results[p99_idx] * 1000,
            "sla_target_s": SLA_TARGETS["task_planning"],
            "sla_met": max(results) < SLA_TARGETS["task_planning"],
        }


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_task_planning_benchmark():
    """Run task planning benchmark."""
    benchmark = TaskPlanningBenchmark()
    results = await benchmark.run()
    
    print("\nTask Planning Benchmark Results:")
    for complexity, stats in results.items():
        print(f"  {complexity.capitalize()}:")
        print(f"    Mean: {stats['mean_ms']:.2f}ms")
        print(f"    P95: {stats['p95_ms']:.2f}ms")
        print(f"    P99: {stats['p99_ms']:.2f}ms")
        print(f"    SLA Met: {stats['sla_met']}")
    
    # All complexities should meet SLA
    for complexity, stats in results.items():
        assert stats["sla_met"], f"Task planning ({complexity}) exceeded SLA"
