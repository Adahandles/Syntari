"""
Tests for Syntari debugger
"""

import pytest
from src.tools.debugger import (
    SyntariDebugger,
    Breakpoint,
    StackFrame,
    DebugCommand,
    DebugState,
)
from src.interpreter.lexer import tokenize
from src.interpreter.parser import Parser


class TestBreakpoint:
    """Tests for Breakpoint dataclass"""
    
    def test_breakpoint_creation(self):
        """Test creating a breakpoint"""
        bp = Breakpoint(id=1, file="test.syn", line=10)
        assert bp.id == 1
        assert bp.file == "test.syn"
        assert bp.line == 10
        assert bp.enabled
        assert bp.hit_count == 0
    
    def test_breakpoint_string(self):
        """Test breakpoint string representation"""
        bp = Breakpoint(id=1, file="test.syn", line=10)
        assert "test.syn:10" in str(bp)
        assert "enabled" in str(bp)


class TestStackFrame:
    """Tests for StackFrame dataclass"""
    
    def test_stack_frame_creation(self):
        """Test creating a stack frame"""
        frame = StackFrame(
            function_name="main",
            file="test.syn",
            line=5,
            locals={"x": 42}
        )
        assert frame.function_name == "main"
        assert frame.file == "test.syn"
        assert frame.line == 5
        assert frame.locals == {"x": 42}
    
    def test_stack_frame_string(self):
        """Test stack frame string representation"""
        frame = StackFrame(
            function_name="main",
            file="test.syn",
            line=5,
            locals={}
        )
        assert "main" in str(frame)
        assert "test.syn:5" in str(frame)


class TestDebugger:
    """Tests for SyntariDebugger"""
    
    def test_debugger_creation(self):
        """Test creating a debugger"""
        debugger = SyntariDebugger(interactive=False)
        assert debugger.state == DebugState.RUNNING
        assert len(debugger.breakpoints) == 0
        assert len(debugger.call_stack) == 0
    
    def test_set_breakpoint_file_line(self):
        """Test setting breakpoint at file:line"""
        debugger = SyntariDebugger(interactive=False)
        bp_id = debugger.set_breakpoint(file="test.syn", line=10)
        
        assert bp_id == 1
        assert len(debugger.breakpoints) == 1
        assert debugger.breakpoints[1].file == "test.syn"
        assert debugger.breakpoints[1].line == 10
    
    def test_set_breakpoint_function(self):
        """Test setting breakpoint at function"""
        debugger = SyntariDebugger(interactive=False)
        bp_id = debugger.set_breakpoint(function="my_function")
        
        assert bp_id == 1
        assert debugger.breakpoints[1].function == "my_function"
    
    def test_delete_breakpoint(self):
        """Test deleting breakpoint"""
        debugger = SyntariDebugger(interactive=False)
        bp_id = debugger.set_breakpoint(file="test.syn", line=10)
        
        assert len(debugger.breakpoints) == 1
        
        result = debugger.delete_breakpoint(bp_id)
        assert result is True
        assert len(debugger.breakpoints) == 0
    
    def test_delete_nonexistent_breakpoint(self):
        """Test deleting nonexistent breakpoint"""
        debugger = SyntariDebugger(interactive=False)
        result = debugger.delete_breakpoint(999)
        assert result is False
    
    def test_toggle_breakpoint(self):
        """Test enabling/disabling breakpoint"""
        debugger = SyntariDebugger(interactive=False)
        bp_id = debugger.set_breakpoint(file="test.syn", line=10)
        
        bp = debugger.breakpoints[bp_id]
        assert bp.enabled is True
        
        debugger.toggle_breakpoint(bp_id)
        assert bp.enabled is False
        
        debugger.toggle_breakpoint(bp_id)
        assert bp.enabled is True
    
    def test_should_break_at_location(self):
        """Test checking if should break at location"""
        debugger = SyntariDebugger(interactive=False)
        debugger.set_breakpoint(file="test.syn", line=10)
        
        assert debugger.should_break(file="test.syn", line=10) is True
        assert debugger.should_break(file="test.syn", line=11) is False
        assert debugger.should_break(file="other.syn", line=10) is False
    
    def test_should_break_disabled_breakpoint(self):
        """Test that disabled breakpoints don't break"""
        debugger = SyntariDebugger(interactive=False)
        bp_id = debugger.set_breakpoint(file="test.syn", line=10)
        debugger.toggle_breakpoint(bp_id)  # Disable
        
        assert debugger.should_break(file="test.syn", line=10) is False
    
    def test_breakpoint_hit_count(self):
        """Test breakpoint hit counting"""
        debugger = SyntariDebugger(interactive=False)
        bp_id = debugger.set_breakpoint(file="test.syn", line=10)
        
        bp = debugger.breakpoints[bp_id]
        assert bp.hit_count == 0
        
        debugger.should_break(file="test.syn", line=10)
        assert bp.hit_count == 1
        
        debugger.should_break(file="test.syn", line=10)
        assert bp.hit_count == 2
    
    def test_push_pop_frame(self):
        """Test pushing and popping stack frames"""
        debugger = SyntariDebugger(interactive=False)
        
        assert len(debugger.call_stack) == 0
        
        debugger.push_frame("main", "test.syn", 5, {"x": 1})
        assert len(debugger.call_stack) == 1
        assert debugger.call_stack[0].function_name == "main"
        
        debugger.push_frame("helper", "test.syn", 10, {"y": 2})
        assert len(debugger.call_stack) == 2
        assert debugger.call_stack[1].function_name == "helper"
        
        debugger.pop_frame()
        assert len(debugger.call_stack) == 1
        assert debugger.call_stack[0].function_name == "main"
    
    def test_continue_execution(self):
        """Test continue command"""
        debugger = SyntariDebugger(interactive=False)
        debugger.state = DebugState.PAUSED
        
        debugger.continue_execution()
        assert debugger.state == DebugState.RUNNING
        assert debugger.step_mode is False
    
    def test_step_over(self):
        """Test step over command"""
        debugger = SyntariDebugger(interactive=False)
        debugger.push_frame("main", "test.syn", 5, {})
        
        debugger.step_over()
        assert debugger.state == DebugState.STEPPING
        assert debugger.step_mode is True
        assert debugger.step_depth == 1  # Current depth
    
    def test_step_into(self):
        """Test step into command"""
        debugger = SyntariDebugger(interactive=False)
        
        debugger.step_into()
        assert debugger.state == DebugState.STEPPING
        assert debugger.step_mode is True
        assert debugger.step_depth == -1  # No depth limit
    
    def test_step_out(self):
        """Test step out command"""
        debugger = SyntariDebugger(interactive=False)
        debugger.push_frame("main", "test.syn", 5, {})
        debugger.push_frame("helper", "test.syn", 10, {})
        
        debugger.step_out()
        assert debugger.state == DebugState.STEPPING
        assert debugger.step_mode is True
        assert debugger.step_depth == 1  # One level up
    
    def test_should_pause_when_stepping(self):
        """Test pause logic when stepping"""
        debugger = SyntariDebugger(interactive=False)
        
        # Not stepping - shouldn't pause
        assert debugger.should_pause() is False
        
        # Step into - should pause
        debugger.step_into()
        assert debugger.should_pause() is True
    
    def test_command_parsing_continue(self):
        """Test parsing continue command"""
        debugger = SyntariDebugger(interactive=False)
        debugger.state = DebugState.PAUSED
        
        debugger.process_command("continue")
        assert debugger.state == DebugState.RUNNING
        
        debugger.state = DebugState.PAUSED
        debugger.process_command("c")
        assert debugger.state == DebugState.RUNNING
    
    def test_command_parsing_step(self):
        """Test parsing step commands"""
        debugger = SyntariDebugger(interactive=False)
        
        debugger.process_command("step")
        assert debugger.step_mode is True
        
        debugger.step_mode = False
        debugger.process_command("s")
        assert debugger.step_mode is True
    
    def test_command_parsing_breakpoint(self):
        """Test parsing breakpoint command"""
        debugger = SyntariDebugger(interactive=False)
        
        debugger.process_command("break test.syn:10")
        assert len(debugger.breakpoints) == 1
        assert debugger.breakpoints[1].file == "test.syn"
        assert debugger.breakpoints[1].line == 10
    
    def test_command_parsing_delete(self):
        """Test parsing delete command"""
        debugger = SyntariDebugger(interactive=False)
        bp_id = debugger.set_breakpoint(file="test.syn", line=10)
        
        debugger.process_command(f"delete {bp_id}")
        assert len(debugger.breakpoints) == 0
    
    def test_multiple_breakpoints(self):
        """Test managing multiple breakpoints"""
        debugger = SyntariDebugger(interactive=False)
        
        bp1 = debugger.set_breakpoint(file="test.syn", line=10)
        bp2 = debugger.set_breakpoint(file="test.syn", line=20)
        bp3 = debugger.set_breakpoint(function="my_function")
        
        assert len(debugger.breakpoints) == 3
        assert bp1 == 1
        assert bp2 == 2
        assert bp3 == 3
        
        debugger.delete_breakpoint(bp2)
        assert len(debugger.breakpoints) == 2
        assert bp2 not in debugger.breakpoints


class TestDebuggerIntegration:
    """Integration tests with interpreter"""
    
    def test_debugger_with_simple_program(self):
        """Test debugger with simple program"""
        code = """
        let x = 5
        print(x)
        """
        
        tokens = tokenize(code)
        tree = Parser(tokens).parse()
        
        debugger = SyntariDebugger(interactive=False)
        debugger.set_breakpoint(line=2)
        
        # Should have one breakpoint
        assert len(debugger.breakpoints) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
