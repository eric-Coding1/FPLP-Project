#!/usr/bin/env python3
"""FPLP Language - Main Entry Point (REPL + File Runner)"""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Add venv site-packages so Pillow is available
_venv_site = os.path.expanduser(
    "~/.workbuddy/binaries/python/envs/default/Lib/site-packages"
)
if os.path.isdir(_venv_site):
    sys.path.insert(0, _venv_site)

from fplp.lexer import Lexer
from fplp.parser import Parser, ParserError
from fplp.compiler import compile_program, CompilerError
from fplp.vm import VM, VMError
from fplp.environment import Environment
from fplp.builtins import FPLPError


def _format_value(val):
    """Format a value for display."""
    if val is None:
        return "nil"
    if isinstance(val, bool):
        return "true" if val else "false"
    if isinstance(val, float):
        if val == int(val):
            return str(int(val))
        return str(val)
    if isinstance(val, list):
        items = ', '.join(_format_value(v) for v in val)
        return '[' + items + ']'
    if isinstance(val, dict):
        items = ', '.join(f'{_format_value(k)}: {_format_value(v)}' for k, v in val.items())
        return '{' + items + '}'
    if isinstance(val, str):
        return '"' + val + '"'
    return str(val)


def run_source(source, env=None):
    """Compile + execute via bytecode VM. Falls back to tree-walk evaluator."""
    if env is None:
        env = Environment()

    lexer = Lexer(source)
    parser = Parser(lexer)
    try:
        program = parser.parse_program()
    except ParserError as e:
        return f"Parse error: {e}"

    # Compile to bytecode
    try:
        code = compile_program(program)
    except CompilerError as e:
        return f"Compile error: {e}"

    # Execute via VM
    try:
        vm = VM()
        result = vm.run_code(code, env)
    except (VMError, FPLPError) as e:
        return f"Runtime error: {e}"
    except Exception as e:
        return f"Unexpected error: {e}"

    if result is not None:
        return _format_value(result)
    return None


def run_file(path):
    """Run a .fplp file."""
    if not os.path.exists(path):
        print(f"Error: file not found: {path}")
        return 1

    with open(path, 'r', encoding='utf-8') as f:
        source = f.read()

    env = Environment()
    result = run_source(source, env)

    if isinstance(result, str):
        print(result)
        return 1
    return 0


def repl():
    """Start interactive REPL."""
    print("╔══════════════════════════════╗")
    print("║   FPLP v1.0 - Fast Parallel ║")
    print("║   Language Plus * Bytecode   ║")
    print("║                              ║")
    print("║   Type 'exit' to quit        ║")
    print("╚══════════════════════════════╝")
    print()

    env = Environment()
    try:
        import readline
    except ImportError:
        pass

    while True:
        try:
            line = input("fplp> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break

        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "exit":
            break

        result = run_source(line, env)
        if result is not None:
            print(result)


def main():
    # Default: launch GUI
    # Flags:
    #   --cli         CLI REPL
    #   --py          Transpile to Python and execute (accelerated, 10x+)
    #   --py-out      Output generated Python code and exit
    args = [a for a in sys.argv[1:] if a]

    if '--py-out' in args:
        args.remove('--py-out')
        if args:
            from fplp.py_gen import transpile_to_py
            with open(args[0], 'r', encoding='utf-8') as f:
                print(transpile_to_py(f.read()))
        else:
            print("Usage: python main.py --py-out <file.fplp>")
        return

    if '--py' in args:
        args.remove('--py')
        if args:
            from fplp.py_gen import exec_fplp
            path = args[0]
            if not os.path.exists(path):
                print(f"Error: file not found: {path}")
                sys.exit(1)
            with open(path, 'r', encoding='utf-8') as f:
                exec_fplp(f.read())
        else:
            print("Usage: python main.py --py <file.fplp>")
        return

    if '--cli' in args:
        args.remove('--cli')
        if args:
            sys.exit(run_file(args[0]))
        else:
            repl()
    elif args:
        sys.exit(run_file(args[0]))
    else:
        try:
            from fplp.gui import launch_gui
            launch_gui()
        except ImportError as e:
            print(f"GUI not available ({e}), falling back to REPL")
            repl()


if __name__ == "__main__":
    main()
