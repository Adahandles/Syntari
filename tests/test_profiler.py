"""
Comprehensive tests for src/tools/profiler.py
"""

import pytest
import json
import tempfile
from pathlib import Path

from src.tools.profiler import (
    FunctionProfile,
    ProfilerStats,
    Profiler,
)


class TestFunctionProfile:
    """Test FunctionProfile data class"""

    def test_function_profile_creation(self):
        """Test creating a function profile"""
        profile = FunctionProfile(name="test_func")
        assert profile.name == "test_func"
        assert profile.call_count == 0
        assert profile.total_time == 0.0

    def test_avg_time_calculation(self):
        """Test average time calculation"""
        profile = FunctionProfile(name="test_func", call_count=5, total_time=10.0)
        assert profile.avg_time == 2.0

    def test_avg_time_zero_calls(self):
        """Test average time with zero calls"""
        profile = FunctionProfile(name="test_func", call_count=0, total_time=0.0)
        assert profile.avg_time == 0.0

    def test_function_profile_attributes(self):
        """Test all function profile attributes"""
        profile = FunctionProfile(
            name="my_func",
            call_count=10,
            total_time=5.0,
            self_time=3.0,
            min_time=0.1,
            max_time=1.0,
            memory_allocated=1024,
            instructions_executed=500,
        )
        assert profile.name == "my_func"
        assert profile.call_count == 10
        assert profile.total_time == 5.0
        assert profile.self_time == 3.0
        assert profile.min_time == 0.1
        assert profile.max_time == 1.0
        assert profile.memory_allocated == 1024
        assert profile.instructions_executed == 500


class TestProfilerStats:
    """Test ProfilerStats class"""

    def test_stats_creation(self):
        """Test creating profiler stats"""
        stats = ProfilerStats()
        assert stats.total_execution_time == 0.0
        assert stats.total_instructions == 0
        assert stats.max_stack_depth == 0
        assert len(stats.functions) == 0

    def test_add_function_call(self):
        """Test adding function call"""
        stats = ProfilerStats()
        stats.add_function_call("func1", 1.5, 100)

        assert "func1" in stats.functions
        profile = stats.functions["func1"]
        assert profile.call_count == 1
        assert profile.total_time == 1.5
        assert profile.min_time == 1.5
        assert profile.max_time == 1.5
        assert profile.instructions_executed == 100

    def test_add_multiple_calls_same_function(self):
        """Test multiple calls to same function"""
        stats = ProfilerStats()
        stats.add_function_call("func1", 1.0, 50)
        stats.add_function_call("func1", 2.0, 100)
        stats.add_function_call("func1", 0.5, 25)

        profile = stats.functions["func1"]
        assert profile.call_count == 3
        assert profile.total_time == 3.5
        assert profile.min_time == 0.5
        assert profile.max_time == 2.0
        assert profile.instructions_executed == 175

    def test_record_opcode(self):
        """Test recording opcode execution"""
        stats = ProfilerStats()
        stats.record_opcode("LOAD")
        stats.record_opcode("LOAD")
        stats.record_opcode("ADD")

        assert stats.opcode_counts["LOAD"] == 2
        assert stats.opcode_counts["ADD"] == 1
        assert stats.total_instructions == 3

    def test_record_line(self):
        """Test recording line execution"""
        stats = ProfilerStats()
        stats.record_line(10)
        stats.record_line(10)
        stats.record_line(20)

        assert stats.line_execution_counts[10] == 2
        assert stats.line_execution_counts[20] == 1

    def test_get_hot_functions(self):
        """Test getting hot functions"""
        stats = ProfilerStats()
        stats.add_function_call("slow", 5.0, 100)
        stats.add_function_call("medium", 2.0, 50)
        stats.add_function_call("fast", 0.5, 10)

        hot_funcs = stats.get_hot_functions(2)
        assert len(hot_funcs) == 2
        assert hot_funcs[0].name == "slow"
        assert hot_funcs[1].name == "medium"

    def test_get_hot_lines(self):
        """Test getting hot lines"""
        stats = ProfilerStats()
        stats.record_line(10)
        stats.record_line(10)
        stats.record_line(10)
        stats.record_line(20)
        stats.record_line(30)

        hot_lines = stats.get_hot_lines(2)
        assert len(hot_lines) == 2
        assert hot_lines[0] == (10, 3)
        assert hot_lines[1] == (20, 1)

    def test_get_hot_opcodes(self):
        """Test getting hot opcodes"""
        stats = ProfilerStats()
        stats.record_opcode("LOAD")
        stats.record_opcode("LOAD")
        stats.record_opcode("LOAD")
        stats.record_opcode("ADD")
        stats.record_opcode("SUB")

        hot_opcodes = stats.get_hot_opcodes(2)
        assert len(hot_opcodes) == 2
        assert hot_opcodes[0] == ("LOAD", 3)
        assert hot_opcodes[1] == ("ADD", 1)


class TestProfiler:
    """Test Profiler class"""

    def test_profiler_creation(self):
        """Test creating profiler"""
        profiler = Profiler()
        assert profiler.enable_line_profiling is True
        assert profiler.enable_memory_profiling is False
        assert profiler.start_time is None

    def test_profiler_with_options(self):
        """Test profiler with custom options"""
        profiler = Profiler(enable_line_profiling=False, enable_memory_profiling=True)
        assert profiler.enable_line_profiling is False
        assert profiler.enable_memory_profiling is True

    def test_start_stop(self):
        """Test start and stop profiling"""
        profiler = Profiler()
        profiler.start()
        assert profiler.start_time is not None

        import time
        time.sleep(0.01)  # Small delay
        profiler.stop()

        assert profiler.stats.total_execution_time > 0

    def test_enter_exit_function(self):
        """Test function enter/exit tracking"""
        profiler = Profiler()
        profiler.start()

        profiler.enter_function("test_func")
        import time
        time.sleep(0.01)
        profiler.exit_function()

        assert "test_func" in profiler.stats.functions
        assert profiler.stats.functions["test_func"].call_count == 1

    def test_nested_function_calls(self):
        """Test nested function calls"""
        profiler = Profiler()
        profiler.start()

        profiler.enter_function("outer")
        profiler.enter_function("inner")
        profiler.exit_function()  # Exit inner
        profiler.exit_function()  # Exit outer

        assert "outer" in profiler.stats.functions
        assert "inner" in profiler.stats.functions

    def test_record_opcode(self):
        """Test recording opcodes"""
        profiler = Profiler()
        profiler.record_opcode("LOAD", 10)

        assert profiler.stats.opcode_counts["LOAD"] == 1
        assert profiler.stats.line_execution_counts[10] == 1

    def test_record_opcode_without_line_profiling(self):
        """Test recording opcodes without line profiling"""
        profiler = Profiler(enable_line_profiling=False)
        profiler.record_opcode("LOAD", 10)

        assert profiler.stats.opcode_counts["LOAD"] == 1
        assert 10 not in profiler.stats.line_execution_counts

    def test_update_stack_depth(self):
        """Test updating stack depth"""
        profiler = Profiler()
        profiler.update_stack_depth(5)
        profiler.update_stack_depth(3)
        profiler.update_stack_depth(10)

        assert profiler.stats.max_stack_depth == 10

    def test_generate_text_report(self):
        """Test generating text report"""
        profiler = Profiler()
        profiler.start()
        profiler.stats.add_function_call("test_func", 1.0, 100)
        profiler.stats.record_opcode("LOAD")
        profiler.stats.record_line(10)
        profiler.stop()

        report = profiler.generate_report("text")
        assert "SYNTARI PERFORMANCE PROFILE" in report
        assert "test_func" in report
        assert "LOAD" in report

    def test_generate_json_report(self):
        """Test generating JSON report"""
        profiler = Profiler()
        profiler.start()
        profiler.stats.add_function_call("test_func", 1.0, 100)
        profiler.stop()

        report = profiler.generate_report("json")
        data = json.loads(report)

        assert "execution_time" in data
        assert "total_instructions" in data
        assert "functions" in data
        assert len(data["functions"]) > 0

    def test_generate_html_report(self):
        """Test generating HTML report"""
        profiler = Profiler()
        profiler.start()
        profiler.stats.add_function_call("test_func", 1.0, 100)
        profiler.stop()

        report = profiler.generate_report("html")
        assert "<!DOCTYPE html>" in report
        assert "Syntari Performance Profile" in report
        assert "test_func" in report

    def test_generate_html_report_with_lines_and_opcodes(self):
        """Test HTML report with hot lines and opcodes"""
        profiler = Profiler(enable_line_profiling=True)
        profiler.start()
        profiler.stats.add_function_call("test_func", 1.0, 100)
        profiler.stats.record_opcode("LOAD")
        profiler.stats.record_opcode("LOAD")
        profiler.stats.record_line(10)
        profiler.stats.record_line(10)
        profiler.stats.record_line(20)
        profiler.stop()

        report = profiler.generate_report("html")
        assert "test_func" in report
        assert "LOAD" in report

    def test_save_report(self):
        """Test saving report to file"""
        profiler = Profiler()
        profiler.start()
        profiler.stats.add_function_call("test_func", 1.0, 100)
        profiler.stop()

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
            temp_file = f.name

        try:
            profiler.save_report(temp_file, "text")
            assert Path(temp_file).exists()

            content = Path(temp_file).read_text()
            assert "test_func" in content
        finally:
            Path(temp_file).unlink(missing_ok=True)

    def test_empty_stats_report(self):
        """Test generating report with no data"""
        profiler = Profiler()
        profiler.start()
        profiler.stop()

        report = profiler.generate_report("text")
        assert "SYNTARI PERFORMANCE PROFILE" in report
        assert profiler.stats.total_instructions == 0

    def test_call_stack_empty_exit(self):
        """Test exiting function with empty call stack"""
        profiler = Profiler()
        profiler.exit_function()  # Should not crash
        assert len(profiler.call_stack) == 0

    def test_profile_interpreter_function(self):
        """Test profile_interpreter main function"""
        from src.tools.profiler import profile_interpreter
        import tempfile
        
        # Create a simple test file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.syn', delete=False) as f:
            f.write('let x = 42\nx')
            temp_file = f.name
        
        try:
            # Test with text format (default)
            profile_interpreter(temp_file, "text", None)
            
            # Test with json format and output file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as out:
                output_file = out.name
            
            try:
                profile_interpreter(temp_file, "json", output_file)
                assert Path(output_file).exists()
            finally:
                Path(output_file).unlink(missing_ok=True)
        finally:
            Path(temp_file).unlink(missing_ok=True)
