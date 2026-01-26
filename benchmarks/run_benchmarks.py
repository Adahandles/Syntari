#!/usr/bin/env python3
"""
Syntari Benchmark Suite

Runs performance benchmarks and generates comparison reports.
"""

import os
import sys
import time
import json
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.interpreter.lexer import tokenize
from src.interpreter.parser import Parser
from src.interpreter.interpreter import Interpreter
from src.tools.profiler import Profiler


@dataclass
class BenchmarkResult:
    """Result of a single benchmark run"""
    name: str
    execution_time: float
    instructions: int
    max_stack_depth: int
    instructions_per_second: float
    success: bool
    error: str = ""


class BenchmarkRunner:
    """Runs benchmarks and collects results"""
    
    def __init__(self, benchmark_dir: str = "."):
        self.benchmark_dir = Path(benchmark_dir)
        self.results: List[BenchmarkResult] = []
    
    def discover_benchmarks(self) -> List[Path]:
        """Discover all .syn benchmark files"""
        benchmarks = list(self.benchmark_dir.glob("*.syn"))
        benchmarks.sort()
        return benchmarks
    
    def run_benchmark(self, filepath: Path) -> BenchmarkResult:
        """Run a single benchmark"""
        print(f"  Running {filepath.name}...", end=" ")
        
        try:
            # Read source
            with open(filepath, 'r', encoding='utf-8') as f:
                source = f.read()
            
            # Parse
            tokens = tokenize(source)
            ast = Parser(tokens).parse()
            
            # Create profiler
            profiler = Profiler(enable_line_profiling=False)
            
            # Create interpreter
            interpreter = Interpreter()
            
            # Monkey-patch for profiling
            original_execute = interpreter._execute
            
            def profiled_execute(node):
                profiler.record_opcode(type(node).__name__)
                profiler.update_stack_depth(len(interpreter.locals))
                return original_execute(node)
            
            interpreter._execute = profiled_execute
            
            # Suppress output during benchmark
            import io
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            # Run benchmark
            profiler.start()
            interpreter.interpret(ast)
            profiler.stop()
            
            # Restore output
            sys.stdout = old_stdout
            
            # Calculate metrics
            exec_time = profiler.stats.total_execution_time
            instructions = profiler.stats.total_instructions
            ips = instructions / exec_time if exec_time > 0 else 0
            
            print(f"✓ {exec_time:.4f}s ({instructions:,} instructions, {ips:,.0f} inst/s)")
            
            return BenchmarkResult(
                name=filepath.stem,
                execution_time=exec_time,
                instructions=instructions,
                max_stack_depth=profiler.stats.max_stack_depth,
                instructions_per_second=ips,
                success=True
            )
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return BenchmarkResult(
                name=filepath.stem,
                execution_time=0.0,
                instructions=0,
                max_stack_depth=0,
                instructions_per_second=0.0,
                success=False,
                error=str(e)
            )
    
    def run_all(self) -> List[BenchmarkResult]:
        """Run all benchmarks"""
        benchmarks = self.discover_benchmarks()
        
        if not benchmarks:
            print("No benchmarks found!")
            return []
        
        print(f"\n{'='*80}")
        print(f"Running {len(benchmarks)} benchmarks...")
        print(f"{'='*80}\n")
        
        for benchmark in benchmarks:
            result = self.run_benchmark(benchmark)
            self.results.append(result)
        
        return self.results
    
    def generate_report(self) -> str:
        """Generate text report"""
        lines = []
        lines.append("\n" + "="*80)
        lines.append("BENCHMARK RESULTS")
        lines.append("="*80)
        lines.append("")
        
        # Summary table
        lines.append(f"{'Benchmark':<25} {'Time (s)':>12} {'Instructions':>15} {'Inst/s':>15} {'Status':>10}")
        lines.append("-"*80)
        
        total_time = 0.0
        total_instructions = 0
        success_count = 0
        
        for result in self.results:
            if result.success:
                status = "✓ PASS"
                total_time += result.execution_time
                total_instructions += result.instructions
                success_count += 1
            else:
                status = "✗ FAIL"
            
            lines.append(
                f"{result.name:<25} "
                f"{result.execution_time:>12.4f} "
                f"{result.instructions:>15,} "
                f"{result.instructions_per_second:>15,.0f} "
                f"{status:>10}"
            )
        
        lines.append("-"*80)
        lines.append(f"{'TOTAL':<25} {total_time:>12.4f} {total_instructions:>15,} {'':<15} {success_count}/{len(self.results)} PASS")
        lines.append("")
        
        # Fastest/slowest
        if self.results:
            successful = [r for r in self.results if r.success]
            if successful:
                fastest = min(successful, key=lambda r: r.execution_time)
                slowest = max(successful, key=lambda r: r.execution_time)
                
                lines.append("Performance Summary:")
                lines.append(f"  Fastest: {fastest.name} ({fastest.execution_time:.4f}s)")
                lines.append(f"  Slowest: {slowest.name} ({slowest.execution_time:.4f}s)")
                lines.append(f"  Average: {total_time/len(successful):.4f}s")
                lines.append("")
        
        lines.append("="*80)
        return "\n".join(lines)
    
    def save_json(self, filename: str):
        """Save results as JSON"""
        data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_benchmarks": len(self.results),
            "successful": len([r for r in self.results if r.success]),
            "failed": len([r for r in self.results if not r.success]),
            "total_time": sum(r.execution_time for r in self.results if r.success),
            "total_instructions": sum(r.instructions for r in self.results if r.success),
            "results": [asdict(r) for r in self.results]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"\nResults saved to {filename}")


def compare_results(file1: str, file2: str):
    """Compare two benchmark result files"""
    with open(file1) as f:
        data1 = json.load(f)
    with open(file2) as f:
        data2 = json.load(f)
    
    print("\n" + "="*80)
    print("BENCHMARK COMPARISON")
    print("="*80)
    print(f"\nBaseline: {file1}")
    print(f"Current:  {file2}")
    print("")
    
    results1 = {r['name']: r for r in data1['results']}
    results2 = {r['name']: r for r in data2['results']}
    
    print(f"{'Benchmark':<25} {'Baseline':>12} {'Current':>12} {'Change':>12} {'Status':>10}")
    print("-"*80)
    
    for name in sorted(results1.keys()):
        if name in results2:
            r1 = results1[name]
            r2 = results2[name]
            
            if r1['success'] and r2['success']:
                change = ((r2['execution_time'] - r1['execution_time']) / r1['execution_time']) * 100
                
                if change < -5:
                    status = "🚀 FASTER"
                elif change > 5:
                    status = "🐌 SLOWER"
                else:
                    status = "≈ SAME"
                
                print(
                    f"{name:<25} "
                    f"{r1['execution_time']:>12.4f} "
                    f"{r2['execution_time']:>12.4f} "
                    f"{change:>11.1f}% "
                    f"{status:>10}"
                )
    
    print("="*80)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        if len(sys.argv) < 4:
            print("Usage: python run_benchmarks.py compare <baseline.json> <current.json>")
            sys.exit(1)
        compare_results(sys.argv[2], sys.argv[3])
    else:
        runner = BenchmarkRunner()
        runner.run_all()
        print(runner.generate_report())
        
        # Save results
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"benchmark_results_{timestamp}.json"
        runner.save_json(output_file)
