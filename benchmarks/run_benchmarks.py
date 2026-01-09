#!/usr/bin/env python3
"""Run all performance benchmarks and generate report."""

import asyncio
import json
import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.config import RESULTS_DIR, SLA_TARGETS
from benchmarks.bench_agent_startup import AgentStartupBenchmark
from benchmarks.bench_task_planning import TaskPlanningBenchmark
from benchmarks.bench_memory_ops import MemoryOperationsBenchmark


async def run_all_benchmarks():
    """Run all benchmarks and collect results."""
    print("=" * 60)
    print("Agile-PM Performance Benchmark Suite")
    print(f"Started at: {datetime.now().isoformat()}")
    print("=" * 60)

    all_results = {
        "timestamp": datetime.now().isoformat(),
        "sla_targets": SLA_TARGETS,
        "benchmarks": {},
    }

    # Agent Startup
    print("\n🚀 Running Agent Startup Benchmark...")
    benchmark = AgentStartupBenchmark()
    results = await benchmark.run()
    all_results["benchmarks"]["agent_startup"] = results
    print(f"   Mean: {results['mean_ms']:.2f}ms | P99: {results['p99_ms']:.2f}ms | SLA: {'✅' if results['sla_met'] else '❌'}")

    # Task Planning
    print("\n📋 Running Task Planning Benchmark...")
    benchmark = TaskPlanningBenchmark()
    results = await benchmark.run()
    all_results["benchmarks"]["task_planning"] = results
    for complexity, stats in results.items():
        print(f"   {complexity}: Mean {stats['mean_ms']:.2f}ms | P99: {stats['p99_ms']:.2f}ms | SLA: {'✅' if stats['sla_met'] else '❌'}")

    # Memory Operations
    print("\n💾 Running Memory Operations Benchmark...")
    benchmark = MemoryOperationsBenchmark()
    results = await benchmark.run()
    all_results["benchmarks"]["memory_ops"] = results
    for op, stats in results.items():
        print(f"   {op}: Mean {stats['mean_ms']:.2f}ms | P99: {stats['p99_ms']:.2f}ms | SLA: {'✅' if stats['sla_met'] else '❌'}")

    # Save results
    os.makedirs(RESULTS_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = os.path.join(RESULTS_DIR, f"benchmark_{timestamp}.json")
    
    with open(results_file, "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n📊 Results saved to: {results_file}")
    
    # Summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    
    all_slas_met = True
    for bench_name, bench_results in all_results["benchmarks"].items():
        if isinstance(bench_results, dict) and "sla_met" in bench_results:
            if not bench_results["sla_met"]:
                all_slas_met = False
        elif isinstance(bench_results, dict):
            for sub_results in bench_results.values():
                if isinstance(sub_results, dict) and not sub_results.get("sla_met", True):
                    all_slas_met = False
    
    print(f"\nAll SLAs Met: {'✅ YES' if all_slas_met else '❌ NO'}")
    print("=" * 60)
    
    return all_slas_met


if __name__ == "__main__":
    success = asyncio.run(run_all_benchmarks())
    sys.exit(0 if success else 1)
