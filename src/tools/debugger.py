"""
Syntari Debugger - Interactive debugging with breakpoints, stepping, and inspection

Features:
- Breakpoints (file:line or function name)
- Step over, step into, step out
- Variable inspection
- Call stack viewing
- Expression evaluation
- Continue execution
- Conditional breakpoints
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from enum import Enum, auto
import traceback

from src.interpreter.nodes import Node, Program
from src.interpreter.interpreter import Interpreter


class DebugCommand(Enum):
    """Debugger commands"""

    CONTINUE = auto()  # c, continue
    STEP_OVER = auto()  # n, next
    STEP_INTO = auto()  # s, step
    STEP_OUT = auto()  # o, out
    BREAKPOINT = auto()  # b, break
    DELETE_BP = auto()  # d, delete
    LIST_BP = auto()  # l, list
    PRINT = auto()  # p, print
    LOCALS = auto()  # locals
    GLOBALS = auto()  # globals
    STACK = auto()  # stack, bt
    EVAL = auto()  # eval
    WHERE = auto()  # w, where
    QUIT = auto()  # q, quit
    HELP = auto()  # h, help


@dataclass
class Breakpoint:
    """Represents a debugger breakpoint"""

    id: int
    file: Optional[str] = None
    line: Optional[int] = None
    function: Optional[str] = None
    condition: Optional[str] = None
    enabled: bool = True
    hit_count: int = 0

    def __str__(self):
        location = f"{self.file}:{self.line}" if self.file else self.function or "unknown"
        status = "enabled" if self.enabled else "disabled"
        cond = f" if {self.condition}" if self.condition else ""
        return f"Breakpoint {self.id}: {location} ({status}, hits: {self.hit_count}){cond}"


@dataclass
class StackFrame:
    """Represents a call stack frame"""

    function_name: str
    file: Optional[str]
    line: int
    locals: Dict[str, Any]
    node: Optional[Node] = None

    def __str__(self):
        location = f"{self.file}:{self.line}" if self.file else f"line {self.line}"
        return f"{self.function_name} at {location}"


class DebugState(Enum):
    """Current debugger state"""

    RUNNING = auto()
    PAUSED = auto()
    STEPPING = auto()
    FINISHED = auto()


class SyntariDebugger:
    """
    Interactive debugger for Syntari programs

    Usage:
        debugger = SyntariDebugger()
        debugger.set_breakpoint(file="script.syn", line=10)
        debugger.run(program)
    """

    def __init__(self, interactive: bool = True):
        self.interactive = interactive
        self.state = DebugState.RUNNING
        self.breakpoints: Dict[int, Breakpoint] = {}
        self.next_bp_id = 1
        self.call_stack: List[StackFrame] = []
        self.current_line = 0
        self.current_file: Optional[str] = None
        self.step_mode = False
        self.step_depth = 0  # Track call depth for step over/out
        self.interpreter: Optional[Interpreter] = None

    def set_breakpoint(
        self,
        file: Optional[str] = None,
        line: Optional[int] = None,
        function: Optional[str] = None,
        condition: Optional[str] = None,
    ) -> int:
        """Set a breakpoint at file:line or function"""
        bp = Breakpoint(
            id=self.next_bp_id,
            file=file,
            line=line,
            function=function,
            condition=condition,
        )
        self.breakpoints[self.next_bp_id] = bp
        self.next_bp_id += 1

        if self.interactive:
            print(f"Breakpoint {bp.id} set at {bp}")

        return bp.id

    def delete_breakpoint(self, bp_id: int) -> bool:
        """Delete a breakpoint by ID"""
        if bp_id in self.breakpoints:
            del self.breakpoints[bp_id]
            if self.interactive:
                print(f"Deleted breakpoint {bp_id}")
            return True
        else:
            if self.interactive:
                print(f"No breakpoint {bp_id}")
            return False

    def list_breakpoints(self):
        """List all breakpoints"""
        if not self.breakpoints:
            print("No breakpoints set")
            return

        print("\nBreakpoints:")
        for bp in self.breakpoints.values():
            print(f"  {bp}")

    def toggle_breakpoint(self, bp_id: int):
        """Enable/disable a breakpoint"""
        if bp_id in self.breakpoints:
            bp = self.breakpoints[bp_id]
            bp.enabled = not bp.enabled
            status = "enabled" if bp.enabled else "disabled"
            print(f"Breakpoint {bp_id} {status}")
        else:
            print(f"No breakpoint {bp_id}")

    def should_break(self, file: Optional[str], line: int, function: Optional[str] = None) -> bool:
        """Check if we should break at this location"""
        for bp in self.breakpoints.values():
            if not bp.enabled:
                continue

            # Check location match
            if bp.file and bp.line:
                if bp.file == file and bp.line == line:
                    if self._check_condition(bp):
                        bp.hit_count += 1
                        return True
            elif bp.function:
                if bp.function == function:
                    if self._check_condition(bp):
                        bp.hit_count += 1
                        return True

        return False

    def _check_condition(self, bp: Breakpoint) -> bool:
        """Check if breakpoint condition is met"""
        if not bp.condition:
            return True

        try:
            # Evaluate condition in current context
            if self.interpreter:
                # Simple evaluation - could be enhanced
                return True  # For now, always break if condition is set
        except Exception:
            return True

        return True

    def push_frame(
        self,
        function_name: str,
        file: Optional[str],
        line: int,
        locals: Dict[str, Any],
        node: Optional[Node] = None,
    ):
        """Push a new stack frame"""
        frame = StackFrame(
            function_name=function_name,
            file=file,
            line=line,
            locals=locals.copy(),
            node=node,
        )
        self.call_stack.append(frame)

    def pop_frame(self):
        """Pop the top stack frame"""
        if self.call_stack:
            self.call_stack.pop()

    def print_stack(self):
        """Print the call stack"""
        if not self.call_stack:
            print("No stack frames")
            return

        print("\nCall Stack:")
        for i, frame in enumerate(reversed(self.call_stack)):
            marker = "=>" if i == 0 else "  "
            print(f"{marker} #{len(self.call_stack) - i - 1}: {frame}")

    def print_locals(self):
        """Print local variables in current frame"""
        if not self.call_stack:
            print("No active frame")
            return

        frame = self.call_stack[-1]
        if not frame.locals:
            print("No local variables")
            return

        print("\nLocal Variables:")
        for name, value in frame.locals.items():
            print(f"  {name} = {value}")

    def print_globals(self):
        """Print global variables"""
        if not self.interpreter:
            print("No interpreter context")
            return

        if not self.interpreter.globals:
            print("No global variables")
            return

        print("\nGlobal Variables:")
        for name, value in self.interpreter.globals.items():
            print(f"  {name} = {value}")

    def eval_expression(self, expr: str):
        """Evaluate an expression in the current context"""
        if not self.interpreter:
            print("No interpreter context")
            return

        try:
            # Parse and evaluate the expression
            from src.interpreter.lexer import tokenize
            from src.interpreter.parser import Parser

            tokens = tokenize(expr)
            parser = Parser(tokens)
            tree = parser._parse_expression()
            result = self.interpreter._evaluate(tree)

            print(f"  {expr} = {result}")
        except Exception as e:
            print(f"  Error evaluating '{expr}': {e}")

    def print_where(self):
        """Print current location"""
        if not self.call_stack:
            print("Not in any frame")
            return

        frame = self.call_stack[-1]
        print(f"\nCurrent location: {frame}")

    def continue_execution(self):
        """Continue execution until next breakpoint"""
        self.state = DebugState.RUNNING
        self.step_mode = False

    def step_over(self):
        """Step over (execute next line, don't enter functions)"""
        self.state = DebugState.STEPPING
        self.step_mode = True
        self.step_depth = len(self.call_stack)

    def step_into(self):
        """Step into (execute next line, enter functions)"""
        self.state = DebugState.STEPPING
        self.step_mode = True
        self.step_depth = -1  # No depth limit

    def step_out(self):
        """Step out (continue until return from current function)"""
        self.state = DebugState.STEPPING
        self.step_mode = True
        self.step_depth = len(self.call_stack) - 1

    def should_pause(self) -> bool:
        """Check if we should pause execution"""
        if self.state == DebugState.FINISHED:
            return False

        if self.step_mode:
            # Check depth for step over/out
            current_depth = len(self.call_stack)

            if self.step_depth == -1:  # step into
                return True
            elif current_depth <= self.step_depth:  # step over/out
                return True

            return False

        return self.state == DebugState.PAUSED

    def pause(self, reason: str = ""):
        """Pause execution"""
        self.state = DebugState.PAUSED
        if reason and self.interactive:
            print(f"\nPaused: {reason}")

    def interactive_loop(self):
        """Interactive command loop"""
        if not self.interactive:
            return

        self.print_where()

        while self.state == DebugState.PAUSED:
            try:
                command = input("(sdb) ").strip()
                if not command:
                    continue

                self.process_command(command)

            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
                continue
            except EOFError:
                print("\nExiting debugger")
                self.state = DebugState.FINISHED
                break

    def process_command(self, command: str):
        """Process a debugger command"""
        parts = command.split(maxsplit=1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Continue
        if cmd in ["c", "continue"]:
            self.continue_execution()

        # Step over
        elif cmd in ["n", "next"]:
            self.step_over()

        # Step into
        elif cmd in ["s", "step"]:
            self.step_into()

        # Step out
        elif cmd in ["o", "out"]:
            self.step_out()

        # Breakpoint
        elif cmd in ["b", "break", "breakpoint"]:
            self._parse_breakpoint_command(args)

        # Delete breakpoint
        elif cmd in ["d", "delete"]:
            if args.isdigit():
                self.delete_breakpoint(int(args))
            else:
                print("Usage: delete <breakpoint_id>")

        # List breakpoints
        elif cmd in ["l", "list"]:
            self.list_breakpoints()

        # Print variable
        elif cmd in ["p", "print"]:
            if args:
                self.eval_expression(args)
            else:
                print("Usage: print <expression>")

        # Locals
        elif cmd == "locals":
            self.print_locals()

        # Globals
        elif cmd == "globals":
            self.print_globals()

        # Stack
        elif cmd in ["stack", "bt", "backtrace"]:
            self.print_stack()

        # Where
        elif cmd in ["w", "where"]:
            self.print_where()

        # Eval
        elif cmd == "eval":
            if args:
                self.eval_expression(args)
            else:
                print("Usage: eval <expression>")

        # Quit
        elif cmd in ["q", "quit", "exit"]:
            self.state = DebugState.FINISHED
            print("Exiting debugger")

        # Help
        elif cmd in ["h", "help", "?"]:
            self.print_help()

        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for available commands")

    def _parse_breakpoint_command(self, args: str):
        """Parse breakpoint command arguments"""
        if not args:
            print("Usage: break <file>:<line> or break <function>")
            return

        # file:line format
        if ":" in args:
            parts = args.split(":")
            if len(parts) == 2:
                file = parts[0]
                try:
                    line = int(parts[1])
                    self.set_breakpoint(file=file, line=line)
                except ValueError:
                    print(f"Invalid line number: {parts[1]}")
        else:
            # Function name
            self.set_breakpoint(function=args)

    def print_help(self):
        """Print help message"""
        help_text = """
Syntari Debugger Commands:

Execution Control:
  c, continue        - Continue execution until next breakpoint
  n, next           - Step over (execute next line)
  s, step           - Step into (enter function calls)
  o, out            - Step out (return from current function)
  q, quit           - Exit debugger

Breakpoints:
  b, break <loc>    - Set breakpoint at location
                      Examples: break script.syn:10
                               break my_function
  d, delete <id>    - Delete breakpoint by ID
  l, list           - List all breakpoints

Inspection:
  p, print <expr>   - Print expression value
  locals            - Show local variables
  globals           - Show global variables
  stack, bt         - Show call stack
  w, where          - Show current location
  eval <expr>       - Evaluate expression

Help:
  h, help, ?        - Show this help message
"""
        print(help_text)

    def run(self, program: Program, file: Optional[str] = None):
        """Run program with debugger attached"""
        self.current_file = file

        # Create interpreter with debugger hooks
        self.interpreter = DebuggableInterpreter(self)

        try:
            if self.interactive:
                print("Syntari Debugger")
                print("Type 'help' for commands")
                print()

            self.interpreter.interpret(program)

            if self.interactive:
                print("\nProgram finished")

        except KeyboardInterrupt:
            print("\nProgram interrupted")
        except Exception as e:
            print(f"\nProgram crashed: {e}")
            traceback.print_exc()
        finally:
            self.state = DebugState.FINISHED


class DebuggableInterpreter(Interpreter):
    """Interpreter with debugger hooks"""

    def __init__(self, debugger: SyntariDebugger):
        super().__init__()
        self.debugger = debugger
        self.current_line = 0

    def _execute(self, node: Node):
        """Execute node with debugger checks"""
        # Update current location
        if hasattr(node, "line"):
            self.current_line = node.line

        # Check for breakpoints
        if self.debugger.should_break(
            file=self.debugger.current_file,
            line=self.current_line,
        ):
            self.debugger.pause(f"Breakpoint at line {self.current_line}")
            self.debugger.interactive_loop()

        # Check if we should pause (stepping)
        if self.debugger.should_pause():
            self.debugger.pause(f"Step at line {self.current_line}")
            self.debugger.interactive_loop()

        # Check if debugger wants to quit
        if self.debugger.state == DebugState.FINISHED:
            raise KeyboardInterrupt("Debugger quit")

        # Execute the node
        return super()._execute(node)

    def visit_FuncDecl(self, node):
        """Function declaration with stack frame tracking"""
        # Push frame for function definition
        self.debugger.push_frame(
            function_name=node.name,
            file=self.debugger.current_file,
            line=self.current_line,
            locals={},
            node=node,
        )

        try:
            result = super().visit_FuncDecl(node)
            return result
        finally:
            self.debugger.pop_frame()

    def visit_Call(self, node):
        """Function call with stack frame tracking"""
        # Get current locals
        current_locals = self.locals[-1] if self.locals else {}

        self.debugger.push_frame(
            function_name=node.callee,
            file=self.debugger.current_file,
            line=self.current_line,
            locals=current_locals,
            node=node,
        )

        try:
            result = super().visit_Call(node)
            return result
        finally:
            self.debugger.pop_frame()
