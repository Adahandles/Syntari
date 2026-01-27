# Syntari Benchmarks

Performance benchmarks for measuring Syntari interpreter efficiency.

## Available Benchmarks

- **fibonacci.syn** - Recursive Fibonacci calculation (tests function calls, recursion)
- **factorial.syn** - Iterative factorial (tests loops, arithmetic)
- **prime_check.syn** - Prime number checking under 1000 (tests conditionals, modulo)
- **array_ops.syn** - Array-like operations (tests accumulation)
- **nested_loops.syn** - Deeply nested loops (tests loop overhead)

## Running Benchmarks

### Run All Benchmarks
```bash
cd benchmarks
python3 run_benchmarks.py
```

### Profile a Single Benchmark
```bash
python3 -m src.tools.profiler benchmarks/fibonacci.syn
```

### Generate HTML Report
```bash
python3 -m src.tools.profiler benchmarks/fibonacci.syn --format html --output profile.html
```

### Compare Results
```bash
# Run baseline
python3 run_benchmarks.py

# Make changes to interpreter
# ...

# Run again
python3 run_benchmarks.py

# Compare
python3 run_benchmarks.py compare benchmark_results_baseline.json benchmark_results_current.json
```

## Performance Metrics

Each benchmark reports:
- **Execution Time** - Total wall-clock time
- **Instructions** - Total instructions executed
- **Inst/s** - Instructions per second
- **Max Stack Depth** - Maximum stack depth reached

## Adding New Benchmarks

1. Create a `.syn` file in `benchmarks/` directory
2. Add a comment header: `// Benchmark: Description`
3. Run `python3 run_benchmarks.py` to include it

## Expected Results (v0.3 Interpreter)

Typical performance on modern hardware:
- Fibonacci(20): ~50-100ms
- Factorial(20): <10ms
- Prime check (1000): ~100-200ms
- Nested loops (50): ~500ms-1s

v0.4 bytecode VM should show 5-10x improvement!
