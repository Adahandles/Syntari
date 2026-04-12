#!/usr/bin/env python3
"""
Syntari Programming Language - Main Entry Point
Provides CLI interface and REPL for Syntari v0.3
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from src.interpreter.lexer import tokenize, LexerError
from src.interpreter.parser import parse, ParseError
from src.interpreter.interpreter import interpret, RuntimeError as SyntariRuntimeError

VERSION = "0.4.0"


def _validate_file_path(path: str, allowed_extensions: Optional[set] = None) -> str:
    """
    Validate and sanitize file path to prevent path traversal attacks.

    Args:
        path: The file path to validate
        allowed_extensions: Set of allowed file extensions (e.g., {'.syn', '.sbc'})

    Returns:
        Resolved absolute path

    Raises:
        ValueError: If path is invalid or contains path traversal attempts
    """
    try:
        # Convert to Path object and resolve to absolute path
        file_path = Path(path).resolve()

        # Check if file exists
        if not file_path.exists():
            raise ValueError(f"File does not exist: {path}")

        # Check if it's a file (not a directory)
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {path}")

        # Check file extension if specified
        if allowed_extensions and file_path.suffix not in allowed_extensions:
            raise ValueError(
                f"Invalid file extension. Expected one of {allowed_extensions}, got {file_path.suffix}"
            )

        return str(file_path)

    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid file path: {e}")


def _validate_output_path(path: str, allowed_extensions: Optional[set] = None) -> str:
    """
    Validate and sanitize output file path to prevent path traversal attacks.

    Args:
        path: The output file path to validate
        allowed_extensions: Set of allowed file extensions

    Returns:
        Resolved absolute path

    Raises:
        ValueError: If path is invalid or contains path traversal attempts
    """
    try:
        # Convert to Path object and resolve to absolute path
        file_path = Path(path).resolve()

        # Check if parent directory exists
        if not file_path.parent.exists():
            raise ValueError(f"Parent directory does not exist: {file_path.parent}")

        # Check file extension if specified
        if allowed_extensions and file_path.suffix not in allowed_extensions:
            raise ValueError(
                f"Invalid file extension. Expected one of {allowed_extensions}, got {file_path.suffix}"
            )

        return str(file_path)

    except (OSError, RuntimeError) as e:
        raise ValueError(f"Invalid output path: {e}")


def run_file(path: str, verbose: bool = False, record_path: Optional[str] = None) -> int:
    """
    Run a Syntari source file

    Args:
        path: Path to .syn file
        verbose: Print verbose output
        record_path: If set, write Chain-Of-Record execution events to this file.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        # Validate file path to prevent path traversal
        validated_path = _validate_file_path(path, allowed_extensions={".syn"})

        # Read source file
        with open(validated_path, "r", encoding="utf-8") as f:
            source = f.read()

        if verbose:
            print(f"[Syntari] Running: {validated_path}")

        # Tokenize
        tokens = tokenize(source)
        if verbose:
            print(f"[Syntari] Tokenized {len(tokens)} tokens")

        # Parse
        tree = parse(tokens)
        if verbose:
            print(f"[Syntari] Parsed AST with {len(tree.statements)} statements")

        # Set up optional Chain-Of-Record adapter
        recorder = None
        if record_path is not None:
            from src.core.chain_of_record import FileAdapter

            recorder = FileAdapter(record_path)
            if verbose:
                print(f"[Syntari] Recording execution events to: {record_path}")

        # Interpret
        try:
            interpret(tree, recorder=recorder)
        finally:
            if recorder is not None:
                recorder.close()
                if verbose:
                    print(f"[Syntari] Wrote {recorder.events_written} events to {record_path}")

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        return 1
    except LexerError as e:
        print(f"Lexer error: {e}", file=sys.stderr)
        return 1
    except ParseError as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return 1
    except SyntariRuntimeError as e:
        print(f"Runtime error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n[Syntari] Interrupted by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if verbose:
            import traceback

            traceback.print_exc()
        return 1


def run_repl() -> int:
    """
    Run interactive REPL (Read-Eval-Print Loop)

    Returns:
        Exit code
    """
    print(f"Syntari v{VERSION} REPL")
    print("Type 'exit' or 'quit' to exit, 'help' for help")
    print()

    # Create persistent interpreter for REPL
    from src.interpreter.interpreter import Interpreter

    interpreter = Interpreter()

    line_num = 1

    while True:
        try:
            # Read input
            try:
                line = input(f"[{line_num}]>>> ")
            except EOFError:
                print("\n[Syntari] Goodbye!")
                return 0

            # Handle special commands
            if line.strip().lower() in ("exit", "quit"):
                print("[Syntari] Goodbye!")
                return 0

            if line.strip().lower() == "help":
                print_help()
                continue

            if line.strip().lower() == "version":
                print(f"Syntari v{VERSION}")
                continue

            if line.strip() == "":
                continue

            # Execute line
            try:
                tokens = tokenize(line)
                tree = parse(tokens)
                result = interpreter.interpret(tree)

                # Print result if not None
                if result is not None:
                    print(f"=> {result}")

                line_num += 1

            except LexerError as e:
                print(f"Lexer error: {e}")
            except ParseError as e:
                print(f"Parse error: {e}")
            except SyntariRuntimeError as e:
                print(f"Runtime error: {e}")

        except KeyboardInterrupt:
            print("\n[Syntari] Use 'exit' or 'quit' to exit")
            continue
        except Exception as e:
            print(f"Unexpected error: {e}")
            import traceback

            traceback.print_exc()


def print_help():
    """Print REPL help"""
    print("""
Syntari REPL Commands:
  help       - Show this help message
  version    - Show Syntari version
  exit/quit  - Exit the REPL
  
You can enter any valid Syntari expression or statement.
Examples:
  print("Hello, world")
  let x = 42
  fn add(a, b) { return a + b }
  add(3, 4)
""")


def compile_file(source_path: str, output_path: Optional[str] = None, verbose: bool = False) -> int:
    """
    Compile Syntari source to bytecode

    Args:
        source_path: Path to .syn file
        output_path: Optional output path for .sbc file
        verbose: Print verbose output

    Returns:
        Exit code
    """
    try:
        # Validate source file path
        validated_source = _validate_file_path(source_path, allowed_extensions={".syn"})

        # Validate output path if provided
        if output_path:
            validated_output = _validate_output_path(output_path, allowed_extensions={".sbc"})
        else:
            # Generate output path from source path
            validated_output = str(Path(validated_source).with_suffix(".sbc"))

        # Import bytecode compiler
        import sys
        import os

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from bytecode import compile_file as bc_compile

        if verbose:
            print(f"[Syntari] Compiling: {validated_source}")

        bc_compile(validated_source, validated_output)

        if verbose:
            print(f"[Syntari] Compiled to: {validated_output}")

        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: File not found: {source_path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Compilation error: {e}", file=sys.stderr)
        if verbose:
            import traceback

            traceback.print_exc()
        return 1


def run_bytecode(path: str, verbose: bool = False) -> int:
    """
    Run compiled Syntari bytecode

    Args:
        path: Path to .sbc file
        verbose: Print verbose output

    Returns:
        Exit code
    """
    try:
        # Validate bytecode file path
        validated_path = _validate_file_path(path, allowed_extensions={".sbc"})

        # Import VM runtime
        import sys
        import os

        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        from runtime import run_vm

        if verbose:
            print(f"[Syntari] Running bytecode: {validated_path}")

        run_vm(validated_path)
        return 0

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except FileNotFoundError:
        print(f"Error: File not found: {path}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"VM error: {e}", file=sys.stderr)
        if verbose:
            import traceback

            traceback.print_exc()
        return 1


def main() -> int:
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Syntari Programming Language Interpreter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  syntari script.syn              # Run a Syntari script
  syntari --repl                  # Start interactive REPL
  syntari --compile script.syn    # Compile to bytecode
  syntari --run script.sbc        # Run bytecode
  syntari --profile script.syn    # Run with performance profiling
  syntari --debug script.syn      # Run with interactive debugger
  syntari --lsp                   # Start LSP server for IDE integration
  syntari --verbose script.syn    # Run with verbose output
  syntari --record script.syn     # Record execution events (Chain-Of-Record)
  syntari --record --record-output audit.jsonl script.syn  # Custom output file
        """,
    )

    parser.add_argument(
        "file", nargs="?", help="Syntari source file (.syn) or bytecode file (.sbc) to run"
    )

    parser.add_argument("-r", "--repl", action="store_true", help="Start interactive REPL")

    parser.add_argument(
        "-c", "--compile", action="store_true", help="Compile source file to bytecode (.sbc)"
    )

    parser.add_argument("--run", action="store_true", help="Run bytecode file (.sbc)")

    parser.add_argument("--profile", action="store_true", help="Run with performance profiling")

    parser.add_argument("--debug", action="store_true", help="Run with interactive debugger")

    parser.add_argument("--lsp", action="store_true", help="Start LSP server for IDE integration")

    parser.add_argument(
        "--profile-format",
        choices=["text", "json", "html"],
        default="text",
        help="Profiler output format (default: text)",
    )

    parser.add_argument("--profile-output", help="Save profiler report to file")

    parser.add_argument("-o", "--output", help="Output file path for compilation")

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument("--version", action="version", version=f"Syntari v{VERSION}")

    parser.add_argument(
        "--record",
        action="store_true",
        help="Record execution events for Chain-Of-Record auditing",
    )

    parser.add_argument(
        "--record-output",
        default="execution_record.jsonl",
        metavar="FILE",
        help="Output file for Chain-Of-Record events (default: execution_record.jsonl)",
    )

    args = parser.parse_args()

    # REPL mode
    if args.repl:
        return run_repl()

    # LSP mode
    if args.lsp:
        try:
            from src.tools.lsp import LSPServer

            print("Starting Syntari LSP server...", file=sys.stderr)
            server = LSPServer()
            server.start()
            return 0
        except Exception as e:
            print(f"LSP server error: {e}", file=sys.stderr)
            if args.verbose:
                import traceback

                traceback.print_exc()
            return 1

    # File required for other modes
    if not args.file:
        parser.print_help()
        return 1

    # Debug mode
    if args.debug:
        try:
            from src.tools.debugger import SyntariDebugger, DebuggableInterpreter

            # Validate and read file
            file_path = _validate_file_path(args.file, {".syn"})
            with open(file_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            # Tokenize and parse
            if args.verbose:
                print(f"Parsing {file_path}...", file=sys.stderr)
            tokens = tokenize(source_code)
            program = parse(tokens)

            # Create debugger and run
            debugger = SyntariDebugger()
            interpreter = DebuggableInterpreter(debugger)
            debugger.run(program, interpreter)
            return 0

        except (LexerError, ParseError, SyntariRuntimeError) as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        except Exception as e:
            print(f"Debug error: {e}", file=sys.stderr)
            if args.verbose:
                import traceback

                traceback.print_exc()
            return 1

    # Profile mode
    if args.profile:
        try:
            from src.tools.profiler import profile_interpreter

            profile_interpreter(args.file, args.profile_format, args.profile_output)
            return 0
        except Exception as e:
            print(f"Profiling error: {e}", file=sys.stderr)
            if args.verbose:
                import traceback

                traceback.print_exc()
            return 1

    # Compile mode
    if args.compile:
        return compile_file(args.file, args.output, args.verbose)

    # Run bytecode mode
    if args.run:
        return run_bytecode(args.file, args.verbose)

    # Default: run source file
    record_path = args.record_output if args.record else None
    return run_file(args.file, args.verbose, record_path=record_path)


if __name__ == "__main__":
    sys.exit(main())
