"""
Syntari Performance Profiler

Tracks execution performance metrics:
- Function call counts and timing
- Memory allocation
- Opcode execution frequency
- Stack depth tracking
- Hot path identification

Usage:
    syntari --profile my_program.syn
    python -m src.tools.profiler my_program.syn
"""

import time
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
import json


@dataclass
class FunctionProfile:
    """Profile data for a single function"""

    name: str
    call_count: int = 0
    total_time: float = 0.0
    self_time: float = 0.0
    min_time: float = float("inf")
    max_time: float = 0.0
    memory_allocated: int = 0
    instructions_executed: int = 0

    @property
    def avg_time(self) -> float:
        """Average time per call"""
        return self.total_time / self.call_count if self.call_count > 0 else 0.0


@dataclass
class ProfilerStats:
    """Overall profiling statistics"""

    total_execution_time: float = 0.0
    total_instructions: int = 0
    max_stack_depth: int = 0
    functions: Dict[str, FunctionProfile] = field(default_factory=dict)
    opcode_counts: Dict[str, int] = field(default_factory=lambda: defaultdict(int))
    line_execution_counts: Dict[int, int] = field(default_factory=lambda: defaultdict(int))

    def add_function_call(self, name: str, duration: float, instructions: int = 0):
        """Record a function call"""
        if name not in self.functions:
            self.functions[name] = FunctionProfile(name)

        profile = self.functions[name]
        profile.call_count += 1
        profile.total_time += duration
        profile.min_time = min(profile.min_time, duration)
        profile.max_time = max(profile.max_time, duration)
        profile.instructions_executed += instructions

    def record_opcode(self, opcode: str):
        """Record opcode execution"""
        self.opcode_counts[opcode] += 1
        self.total_instructions += 1

    def record_line(self, lineno: int):
        """Record line execution"""
        self.line_execution_counts[lineno] += 1

    def get_hot_functions(self, top_n: int = 10) -> List[FunctionProfile]:
        """Get top N functions by total time"""
        return sorted(self.functions.values(), key=lambda f: f.total_time, reverse=True)[:top_n]

    def get_hot_lines(self, top_n: int = 20) -> List[tuple]:
        """Get top N most executed lines"""
        return sorted(self.line_execution_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]

    def get_hot_opcodes(self, top_n: int = 15) -> List[tuple]:
        """Get top N most executed opcodes"""
        return sorted(self.opcode_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]


class Profiler:
    """Performance profiler for Syntari programs"""

    def __init__(self, enable_line_profiling: bool = True, enable_memory_profiling: bool = False):
        self.stats = ProfilerStats()
        self.enable_line_profiling = enable_line_profiling
        self.enable_memory_profiling = enable_memory_profiling
        self.start_time: Optional[float] = None
        self.call_stack: List[tuple] = []  # (function_name, start_time, instructions_at_start)

    def start(self):
        """Start profiling"""
        self.start_time = time.time()
        self.stats = ProfilerStats()

    def stop(self):
        """Stop profiling"""
        if self.start_time:
            self.stats.total_execution_time = time.time() - self.start_time

    def enter_function(self, name: str):
        """Enter a function"""
        self.call_stack.append((name, time.time(), self.stats.total_instructions))

    def exit_function(self):
        """Exit a function"""
        if self.call_stack:
            name, start_time, start_instructions = self.call_stack.pop()
            duration = time.time() - start_time
            instructions = self.stats.total_instructions - start_instructions
            self.stats.add_function_call(name, duration, instructions)

    def record_opcode(self, opcode: str, lineno: int = 0):
        """Record opcode execution"""
        self.stats.record_opcode(opcode)
        if self.enable_line_profiling and lineno > 0:
            self.stats.record_line(lineno)

    def update_stack_depth(self, depth: int):
        """Update maximum stack depth"""
        self.stats.max_stack_depth = max(self.stats.max_stack_depth, depth)

    def generate_report(self, output_format: str = "text") -> str:
        """Generate profiling report"""
        if output_format == "json":
            return self._generate_json_report()
        elif output_format == "html":
            return self._generate_html_report()
        else:
            return self._generate_text_report()

    def _generate_text_report(self) -> str:
        """Generate text report"""
        lines = []
        lines.append("=" * 80)
        lines.append("SYNTARI PERFORMANCE PROFILE")
        lines.append("=" * 80)
        lines.append("")

        # Overall statistics
        lines.append("Overall Statistics:")
        lines.append(f"  Total execution time: {self.stats.total_execution_time:.4f}s")
        lines.append(f"  Total instructions:   {self.stats.total_instructions:,}")
        lines.append(f"  Max stack depth:      {self.stats.max_stack_depth}")
        if self.stats.total_execution_time > 0:
            ips = self.stats.total_instructions / self.stats.total_execution_time
            lines.append(f"  Instructions/second:  {ips:,.0f}")
        lines.append("")

        # Function profiles
        if self.stats.functions:
            lines.append("-" * 80)
            lines.append("Function Profile:")
            lines.append("-" * 80)
            lines.append(
                f"{'Function':<30} {'Calls':>8} {'Total Time':>12} {'Avg Time':>12} {'% Total':>8}"
            )
            lines.append("-" * 80)

            for func in self.stats.get_hot_functions(20):
                pct = (
                    (func.total_time / self.stats.total_execution_time * 100)
                    if self.stats.total_execution_time > 0
                    else 0
                )
                lines.append(
                    f"{func.name:<30} {func.call_count:>8} "
                    f"{func.total_time:>11.4f}s {func.avg_time:>11.4f}s {pct:>7.1f}%"
                )
            lines.append("")

        # Hot lines
        if self.enable_line_profiling and self.stats.line_execution_counts:
            lines.append("-" * 80)
            lines.append("Hot Lines (Most Executed):")
            lines.append("-" * 80)
            lines.append(f"{'Line #':>8} {'Executions':>15} {'% of Total':>12}")
            lines.append("-" * 80)

            for lineno, count in self.stats.get_hot_lines(15):
                pct = (
                    (count / self.stats.total_instructions * 100)
                    if self.stats.total_instructions > 0
                    else 0
                )
                lines.append(f"{lineno:>8} {count:>15,} {pct:>11.2f}%")
            lines.append("")

        # Opcode statistics
        if self.stats.opcode_counts:
            lines.append("-" * 80)
            lines.append("Opcode Statistics:")
            lines.append("-" * 80)
            lines.append(f"{'Opcode':<20} {'Count':>15} {'% of Total':>12}")
            lines.append("-" * 80)

            for opcode, count in self.stats.get_hot_opcodes(15):
                pct = (
                    (count / self.stats.total_instructions * 100)
                    if self.stats.total_instructions > 0
                    else 0
                )
                lines.append(f"{opcode:<20} {count:>15,} {pct:>11.2f}%")
            lines.append("")

        lines.append("=" * 80)
        return "\n".join(lines)

    def _generate_json_report(self) -> str:
        """Generate JSON report"""
        report = {
            "execution_time": self.stats.total_execution_time,
            "total_instructions": self.stats.total_instructions,
            "max_stack_depth": self.stats.max_stack_depth,
            "instructions_per_second": (
                self.stats.total_instructions / self.stats.total_execution_time
                if self.stats.total_execution_time > 0
                else 0
            ),
            "functions": [
                {
                    "name": f.name,
                    "call_count": f.call_count,
                    "total_time": f.total_time,
                    "avg_time": f.avg_time,
                    "min_time": f.min_time if f.min_time != float("inf") else 0,
                    "max_time": f.max_time,
                    "instructions": f.instructions_executed,
                }
                for f in self.stats.get_hot_functions(50)
            ],
            "hot_lines": [
                {"line": line, "count": count} for line, count in self.stats.get_hot_lines(50)
            ],
            "opcodes": [
                {"opcode": op, "count": count} for op, count in self.stats.get_hot_opcodes(30)
            ],
        }
        return json.dumps(report, indent=2)

    def _generate_html_report(self) -> str:
        """Generate HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Syntari Performance Profile</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; border-bottom: 2px solid #ddd; padding-bottom: 8px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 20px 0; }}
        .stat-box {{ background: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #4CAF50; }}
        .stat-label {{ font-size: 0.9em; color: #666; }}
        .stat-value {{ font-size: 1.5em; font-weight: bold; color: #333; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #4CAF50; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px; border-bottom: 1px solid #ddd; }}
        tr:hover {{ background: #f5f5f5; }}
        .bar {{ background: #4CAF50; height: 20px; border-radius: 3px; }}
        .bar-container {{ background: #e0e0e0; height: 20px; border-radius: 3px; overflow: hidden; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Syntari Performance Profile</h1>

        <div class="stats">
            <div class="stat-box">
                <div class="stat-label">Execution Time</div>
                <div class="stat-value">{self.stats.total_execution_time:.4f}s</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Total Instructions</div>
                <div class="stat-value">{self.stats.total_instructions:,}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Max Stack Depth</div>
                <div class="stat-value">{self.stats.max_stack_depth}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Instructions/Second</div>
                <div class="stat-value">{(self.stats.total_instructions / self.stats.total_execution_time if self.stats.total_execution_time > 0 else 0):,.0f}</div>
            </div>
        </div>

        <h2>Function Profile</h2>
        <table>
            <tr>
                <th>Function</th>
                <th>Calls</th>
                <th>Total Time</th>
                <th>Avg Time</th>
                <th>% Total</th>
                <th>Timeline</th>
            </tr>
"""
        for func in self.stats.get_hot_functions(20):
            pct = (
                (func.total_time / self.stats.total_execution_time * 100)
                if self.stats.total_execution_time > 0
                else 0
            )
            html += f"""
            <tr>
                <td><strong>{func.name}</strong></td>
                <td>{func.call_count:,}</td>
                <td>{func.total_time:.4f}s</td>
                <td>{func.avg_time:.4f}s</td>
                <td>{pct:.1f}%</td>
                <td>
                    <div class="bar-container">
                        <div class="bar" style="width: {pct}%"></div>
                    </div>
                </td>
            </tr>
"""

        html += """
        </table>

        <h2>Hot Lines</h2>
        <table>
            <tr>
                <th>Line #</th>
                <th>Executions</th>
                <th>% of Total</th>
            </tr>
"""

        for lineno, count in self.stats.get_hot_lines(15):
            pct = (
                (count / self.stats.total_instructions * 100)
                if self.stats.total_instructions > 0
                else 0
            )
            html += f"""
            <tr>
                <td>{lineno}</td>
                <td>{count:,}</td>
                <td>{pct:.2f}%</td>
            </tr>
"""

        html += """
        </table>

        <h2>Opcode Statistics</h2>
        <table>
            <tr>
                <th>Opcode</th>
                <th>Count</th>
                <th>% of Total</th>
            </tr>
"""

        for opcode, count in self.stats.get_hot_opcodes(15):
            pct = (
                (count / self.stats.total_instructions * 100)
                if self.stats.total_instructions > 0
                else 0
            )
            html += f"""
            <tr>
                <td><code>{opcode}</code></td>
                <td>{count:,}</td>
                <td>{pct:.2f}%</td>
            </tr>
"""

        html += """
        </table>
    </div>
</body>
</html>
"""
        return html

    def save_report(self, filename: str, output_format: str = "text"):
        """Save report to file"""
        report = self.generate_report(output_format)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"[Profiler] Report saved to {filename}")


def profile_interpreter(
    source_file: str, output_format: str = "text", output_file: Optional[str] = None
):
    """Profile interpreter execution"""
    from ..interpreter.lexer import tokenize
    from ..interpreter.parser import Parser
    from ..interpreter.interpreter import Interpreter

    # Read source
    with open(source_file, "r", encoding="utf-8") as f:
        source = f.read()

    # Create profiler
    profiler = Profiler(enable_line_profiling=True)

    # Parse
    tokens = tokenize(source)
    ast = Parser(tokens).parse()

    # Create interpreter with profiling
    interpreter = Interpreter()

    # Monkey-patch interpreter for profiling
    original_execute = interpreter._execute

    def profiled_execute(node):
        profiler.record_opcode(type(node).__name__, getattr(node, "lineno", 0))
        return original_execute(node)

    interpreter._execute = profiled_execute

    # Run with profiling
    print(f"[Profiler] Profiling {source_file}...")
    profiler.start()

    try:
        interpreter.interpret(ast)
    except Exception as e:
        print(f"[Profiler] Execution error: {e}")

    profiler.stop()

    # Generate report
    if output_file:
        profiler.save_report(output_file, output_format)
    else:
        print(profiler.generate_report(output_format))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python -m src.tools.profiler <source.syn> [--format text|json|html] [--output file]"
        )
        print("\nOptions:")
        print("  --format FORMAT   Output format (text, json, html)")
        print("  --output FILE     Save report to file")
        sys.exit(1)

    source = sys.argv[1]
    output_format = "text"
    output_file = None

    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--format" and i + 1 < len(sys.argv):
            output_format = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--output" and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        else:
            i += 1

    profile_interpreter(source, output_format, output_file)
