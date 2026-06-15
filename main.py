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
    print("║   Language Plus ✦ Bytecode  ║")
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


def _benchmark_file(filepath):
    """Benchmark all execution modes for a given file."""
    import time as _time
    import io as _io
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        source = f.read()
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    code = compile_program(program)
    N = 50
    results = []

    # Suppress stdout during benchmark
    old_stdout = sys.stdout
    sys.stdout = _io.StringIO()

    # 1. Native VM
    t0 = _time.perf_counter()
    for _ in range(N):
        VM().run_code(code, Environment())
    t1 = _time.perf_counter()
    results.append(("VM (native)", (t1 - t0) / N * 1000))

    # 2. Python transpiler (cold)
    from fplp.py_gen import transpile_to_py, _wrap_builtins
    t0 = _time.perf_counter()
    for _ in range(N):
        py_code = transpile_to_py(source)
        compiled = compile(py_code, '<fplp>', 'exec')
        env = _wrap_builtins({})
        exec(compiled, env)
    t1 = _time.perf_counter()
    results.append(("Py trans (cold)", (t1 - t0) / N * 1000))

    # 3. Python transpiler (hot)
    py_code = transpile_to_py(source)
    compiled = compile(py_code, '<fplp>', 'exec')
    t0 = _time.perf_counter()
    for _ in range(N):
        env = _wrap_builtins({})
        exec(compiled, env)
    t1 = _time.perf_counter()
    results.append(("Py trans (hot)", (t1 - t0) / N * 1000))

    sys.stdout = old_stdout
    basename = os.path.basename(filepath)
    print('=' * 53)

    print(f"  Benchmark: {basename} ({N} iterations)")
    print('=' * 53)
    best = min(r[1] for r in results)
    for name, ms in results:
        rel = ms / best if best > 0 else 0
        bar = '█' * int(rel * 20) if rel < 50 else '█' * 20 + '→'
        print(f"  {name:<22s} {ms:8.2f}ms {rel:5.1f}x {bar}")
    print('=' * 53)


def main():
    args = [a for a in sys.argv[1:] if a]

    # Package management commands
    if '--install' in args:
        args.remove('--install')
        if args:
            from fplp.pkg import install, make_sample_package
            for name in args:
                if name.startswith('fplp-') or name in ('hello', 'stats', 'colors'):
                    # Try local sample first
                    sample_map = {'hello': 'fplp-hello', 'stats': 'fplp-stats', 'colors': 'fplp-colors'}
                    mapped = sample_map.get(name, name)
                    if mapped.startswith('fplp-'):
                        if not make_sample_package(mapped):
                            install(mapped)
                    else:
                        install(mapped)
                else:
                    install(name)
        else:
            print("Usage: python main.py --install <package-name>")
        return

    if '--pkg-list' in args:
        from fplp.pkg import installed_packages, search_packages
        installed = installed_packages()
        if installed:
            print(f"Installed packages ({len(installed)}):")
            for name, path, mtime, size in installed:
                import datetime
                dt = datetime.datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M')
                print(f"  {name:<20s} {size:>6d}B  {dt}")
        else:
            print("No packages installed. Use --install <name>")
            print("Available: fplp-hello, fplp-stats, fplp-colors")
        return

    if '--pkg-search' in args:
        args.remove('--pkg-search')
        query = ' '.join(args) if args else ''
        from fplp.pkg import search_packages
        results = search_packages(query)
        if results:
            print(f"Found {len(results)} package(s):")
            for name, info in results:
                print(f"  {name:<20s} {info.get('version', '?'):<8s} {info.get('description', '')}")
        else:
            print("No packages found.")
        return

    if '--pkg-load' in args:
        from fplp.pkg import load_installed
        load_installed()
        return

    if '--bench' in args:
        args.remove('--bench')
        filepath = args[0] if args else ''
        if not filepath or not os.path.exists(filepath):
            filepath = os.path.join(os.path.dirname(__file__), "examples", "demo.fplp")
        if not os.path.exists(filepath): return
        _benchmark_file(filepath)
        return

    if '--pyc' in args:
        args.remove('--pyc')
        if args:
            from fplp.py_gen import exec_fplp_cached
            path = args[0]
            if not os.path.exists(path):
                print(f"Error: file not found: {path}")
                sys.exit(1)
            with open(path, 'r', encoding='utf-8') as f:
                exec_fplp_cached(f.read(), path)
        else:
            print("Usage: python main.py --pyc <file.fplp>")
        return

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
        if args: sys.exit(run_file(args[0]))
        else: repl()
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