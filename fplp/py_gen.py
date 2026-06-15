"""FPLP Language → Python Transpiler (JIT-like acceleration)

Transpiles FPLP source to Python bytecode via compilation, giving
near-native Python execution speed (~3-5x over tree-walk interpreter).
"""

import os, sys
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fplp.lexer import Lexer
from fplp.parser import Parser
from fplp.ast_nodes import *
from fplp.builtins import BUILTINS


def transpile_to_py(source):
    """Transpile FPLP source to a Python function that executes it."""
    lexer = Lexer(source)
    parser = Parser(lexer)
    program = parser.parse_program()
    gen = PyGen()
    return gen.generate(program)


def compile_to_pyc(source, output_path=None):
    """Transpile FPLP to Python, then compile to .pyc bytecode."""
    py_code = transpile_to_py(source)
    compiled = compile(py_code, '<fplp>', 'exec')
    if output_path:
        import marshal
        import importlib.util
        with open(output_path, 'wb') as f:
            f.write(importlib.util.MAGIC_NUMBER)
            import struct
            f.write(struct.pack('<I', 0))  # timestamp
            f.write(struct.pack('<I', 0))  # size
            marshal.dump(compiled, f)
    return compiled


def exec_fplp(source, env=None):
    """Transpile FPLP to Python and execute it immediately."""
    py_code = transpile_to_py(source)
    if env is None:
        env = {}

    # Map FPLP builtins to plain Python functions in the exec namespace
    import builtins as _py_builtins
    for name, fn in BUILTINS.items():
        if hasattr(fn, 'call'):
            def make_wrapper(f=fn):
                return lambda *args: f.call(list(args))
            env[name] = make_wrapper()
        elif callable(fn):
            env[name] = fn
        # Skip module dicts (like json, math, os) - they'd need deeper wrapping

    compiled = compile(py_code, '<fplp>', 'exec')
    exec(compiled, env)
    return env


def _wrap_builtins(env):
    """Populate an exec namespace with FPLP builtins as plain Python functions."""
    for name, fn in BUILTINS.items():
        if hasattr(fn, 'call'):
            def make_wrapper(f=fn):
                return lambda *args: f.call(list(args))
            env[name] = make_wrapper()
        elif callable(fn):
            env[name] = fn
    return env


def exec_fplp_cached(source, source_path=None):
    """Like exec_fplp, but caches the compiled Python to disk.

    The .pyc is saved as <source>.fplpyc. If the cache is fresh,
    skips parsing + transpilation entirely and loads bytecode directly.
    """
    import marshal
    import struct
    import importlib.util as _util
    import hashlib

    cache_path = (source_path or '') + '.fplpyc'
    compile_needed = True

    if source_path and os.path.exists(cache_path):
        src_mtime = os.path.getmtime(source_path)
        cache_mtime = os.path.getmtime(cache_path)
        if cache_mtime > src_mtime:
            # Cache looks fresh - try loading it
            try:
                with open(cache_path, 'rb') as f:
                    magic = f.read(4)
                    f.read(4)  # timestamp
                    f.read(4)  # size
                    code = marshal.load(f)
                env = _wrap_builtins({})
                exec(code, env)
                return env
            except Exception:
                pass  # Cache invalid, recompile

    # Compile
    py_code = transpile_to_py(source)
    code = compile(py_code, source_path or '<fplp>', 'exec')

    # Save cache
    if source_path:
        try:
            with open(cache_path, 'wb') as f:
                f.write(_util.MAGIC_NUMBER)
                f.write(struct.pack('<I', int(os.path.getmtime(source_path))))
                f.write(struct.pack('<I', 0))
                marshal.dump(code, f)
        except Exception:
            pass

    env = _wrap_builtins({})
    exec(code, env)
    return env


# ======================================================================
# Python Generator
# ======================================================================

class PyGen:
    def __init__(self):
        self._indent = 0
        self._lines = []
        self._builtin_names = set(BUILTINS.keys())
        self._temp_counter = 0

    def gen(self, program):
        self._lines = []
        self._emit("def _fplp_main():")
        self._indent = 1

        for stmt in program.statements:
            self._emit_stmt(stmt)

        self._indent = 0
        self._emit()
        self._emit("_fplp_main()")
        return '\n'.join(self._lines)

    generate = gen

    def _emit(self, line=""):
        if line:
            self._lines.append("    " * self._indent + line)
        elif not self._lines or self._lines[-1]:
            self._lines.append("")

    def _temp(self):
        self._temp_counter += 1
        return f"__t{self._temp_counter}"

    def _emit_stmt(self, node):
        t = type(node)

        if t is ExpressionStatement:
            code = self._expr(node.expression)
            self._emit(f"{code}")  # bare expression is valid Python

        elif t is LetStatement:
            if isinstance(node.value, FnLiteral):
                fn = node.value
                self._emit_fn(node.name.value, fn.parameters, fn.body)
            else:
                code = self._expr(node.value)
                self._emit(f"{node.name.value} = {code}")

        elif t is AssignStatement:
            code = self._expr(node.value)
            self._emit(f"{node.name} = {code}")

        elif t is ReturnStatement:
            if node.value:
                code = self._expr(node.value)
                self._emit(f"return {code}")
            else:
                self._emit("return None")

        elif t is BlockStatement:
            for s in node.statements:
                self._emit_stmt(s)

        elif t is IfExpression:
            cond = self._expr(node.condition)
            self._emit(f"if {cond}:")
            self._indent += 1
            self._emit_stmt(node.consequence)
            self._indent -= 1
            if node.alternative:
                self._emit("else:")
                self._indent += 1
                self._emit_stmt(node.alternative)
                self._indent -= 1

        elif t is LoopExpression:
            if node.is_while:
                cond = self._expr(node.iterable)
                self._emit(f"while {cond}:")
                self._indent += 1
                self._emit_stmt(node.body)
                self._indent -= 1
            else:
                # for x in iterable { body }
                code = self._expr(node.iterable)
                self._emit(f"for {node.identifier} in {code}:")
                self._indent += 1
                self._emit_stmt(node.body)
                self._indent -= 1

    def _expr(self, node):
        t = type(node)

        if t is Identifier:
            name = node.value
            if name in ('true', 'false', 'nil'):
                return {'true': 'True', 'false': 'False', 'nil': 'None'}[name]
            # Builtins are passed directly to exec namespace
            return name

        elif t is NumberLiteral:
            return str(node.value)

        elif t is StringLiteral:
            escaped = node.value.replace('\\', '\\\\').replace("'", "\\'")
            return f"'{escaped}'"

        elif t is BooleanLiteral:
            return 'True' if node.value else 'False'

        elif t is NilLiteral:
            return 'None'

        elif t is ArrayLiteral:
            els = ", ".join(self._expr(e) for e in node.elements)
            return f"[{els}]"

        elif t is MapLiteral:
            pairs = []
            for k, v in node.pairs.items():
                kcode = self._expr(k)
                vcode = self._expr(v)
                pairs.append(f"{kcode}: {vcode}")
            return "{" + ", ".join(pairs) + "}"

        elif t is PrefixExpression:
            r = self._expr(node.right)
            if node.operator == '-':
                return f"-({r})"
            elif node.operator in ('not', '!'):
                return f"not ({r})"
            return r

        elif t is InfixExpression:
            op = node.operator
            l = self._expr(node.left)
            r = self._expr(node.right)
            if op == 'and':
                return f"({l}) and ({r})"
            elif op == 'or':
                return f"({l}) or ({r})"
            elif op == '=':
                if isinstance(node.left, Identifier):
                    return f"({node.left.value} := {r})"
                return f"({l} = {r})"
            elif op == '==':
                return f"({l}) == ({r})"
            elif op == '!=':
                return f"({l}) != ({r})"
            elif op == '<':
                return f"({l}) < ({r})"
            elif op == '>':
                return f"({l}) > ({r})"
            elif op == '<=':
                return f"({l}) <= ({r})"
            elif op == '>=':
                return f"({l}) >= ({r})"
            else:
                return f"({l}) {op} ({r})"

        elif t is CallExpression:
            fn = self._expr(node.function)
            args = ", ".join(self._expr(a) for a in node.arguments)

            # Builtins are passed to exec namespace directly
            return f"{fn}({args})"

        elif t is IndexExpression:
            obj = self._expr(node.left)
            idx = self._expr(node.index)
            return f"{obj}[{idx}]"

        elif t is FnLiteral:
            params = ", ".join(p.value for p in node.parameters)
            # Generate body as nested function
            body_code = []
            for s in node.body.statements:
                body_code.append(self._expr(s) if isinstance(s, ExpressionStatement) else s)
            return f"lambda {params}: {self._expr(node.body.statements[0].expression) if len(node.body.statements) == 1 and isinstance(node.body.statements[0], ExpressionStatement) else 'None'}"

    def _emit_fn(self, name, params, body):
        params_str = ", ".join(p.value for p in params)
        self._emit(f"def {name}({params_str}):")
        self._indent += 1
        for s in body.statements:
            if isinstance(s, ExpressionStatement):
                # Arrow function: auto-return
                code = self._expr(s.expression)
                self._emit(f"return {code}")
            else:
                self._emit_stmt(s)
        # Add implicit return None if no return
        has_return = any(isinstance(s, ReturnStatement) for s in body.statements)
        if not has_return and not (len(body.statements) == 1 and isinstance(body.statements[0], ExpressionStatement)):
            self._emit("return None")
        self._indent -= 1
        self._emit()
