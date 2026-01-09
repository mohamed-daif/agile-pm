"""Benchmark: Memory Operations."""

import asyncio
import statistics
import time
from typing import List

import pytest

from benchmarks.config import BENCHMARK_ITERATIONS, WARMUP_ITERATIONS, SLA_TARGETS


class MemoryOperationsBenchmark:
    """Benchmark memory read/write operations."""

    def __init__(self):
        self.read_results: List[float] = []
        self.write_results: List[float] = []
        self.memory_store: dict = {}

    async def memory_write(self, key: str, value: dict) -> float:
        """Simulate memory write."""
        start = time.perf_counter()
        
        # Simulated write operation
        await asyncio.sleep(0.005)  # Serialize
        self.memory_store[key] = value
        await asyncio.sleep(0.005)  # Persist
        
        return time.perf_counter() - start

    async def memory_read(self, key: str) -> tuple[dict, float]:
        """Simulate memory read."""
        start = time.perf_counter()
        
        # Simulated read operation
        await asyncio.sleep(0.002)  # Fetch
        value = self.memory_store.get(key, {})
        
        return value, time.perf_counter() - start

    async def run(self, iterations: int = BENCHMARK_ITERATIONS) -> dict:
        """Run memory operations benchmark."""
        # Warmup
        for i in range(WARMUP_ITERATIONS):
            await self.memory_write(f"warmup_{i}", {"data": i})
            await self.memory_read(f"warmup_{i}")

        # Benchmark writes
        write_results = []
        for i in range(iterations):
            elapsed = await self.memory_write(f"bench_{i}", {"iteration": i, "data": "x" * 100})
            write_results.append(elapsed)

        # Benchmark reads
        read_results = []
        for i in range(iterations):
            _, elapsed = await self.memory_read(f"bench_{i}")
            read_results.append(elapsed)

        return {
            "write": self._calc_stats(write_results, "memory_write"),
            "read": self._calc_stats(read_results, "memory_read"),
        }

    def _calc_stats(self, results: List[float], operation: str) -> dict:
        """Calculate statistics."""
        sorted_results = sorted(results)
        p95_idx = int(len(sorted_results) * 0.95)
        p99_idx = int(len(sorted_results) * 0.99)
        
        sla_key = "memory_write" if "write" in operation else "memory_read"

        return {
            "benchmark": operation,
            "iterations": len(results),
            "mean_ms": statistics.mean(results) * 1000,
            "p95_ms": sorted_results[p95_idx] * 1000,
            "p99_ms": sorted_results[p99_idx] * 1000,
            "sla_target_ms": SLA_TARGETS[sla_key] * 1000,
            "sla_met": sorted_results[p99_idx] < SLA_TARGETS[sla_key],
        }


@pytest.mark.benchmark
@pytest.mark.asyncio
async def test_memory_operations_benchmark():
    """Run memory operations benchmark."""
    benchmark = MemoryOperationsBenchmark()
    results = await benchmark.run()
    
    print("\nMemory Operations Benchmark Results:")
    for op, stats in results.items():
        print(f"  {op.capitalize()}:")
        print(f"    Mean: {stats['mean_ms']:.2f}ms")
        print(f"    P95: {stats['p95_ms']:.2f}ms")
        print(f"    P99: {stats['p99_ms']:.2f}ms")
        print(f"    SLA Target: {stats['sla_target_ms']:.0f}ms")
        print(f"    SLA Met: {stats['sla_met']}")
    
    assert results["write"]["sla_met"], "Memory write exceeded SLA"
    assert results["read"]["sla_met"], "Memory read exceeded SLA"
