"""FPLP Language - AST → Bytecode Compiler"""

from .ast_nodes import *
from .bytecode import *
from .builtins import BUILTINS


class CompilerError(Exception):
    pass


class Compiler:
    """Recursively compiles AST nodes into bytecode CodeObjects."""

    def __init__(self):
        self._builtin_names = set(BUILTINS.keys())
        self._temp_counter = 0

    def _temp_name(self):
        """Generate a unique internal variable name."""
        self._temp_counter += 1
        return f"${self._temp_counter}"

    # ----- Entry point -----

    def compile(self, program):
        code = CodeObject("<main>")
        for stmt in program.statements:
            self._emit_stmt(code, stmt)
        code.add_instr(HALT)
        return code

    # ----- Statement dispatch -----

    def _emit_stmt(self, code, node):
        t = type(node)

        if t is ExpressionStatement:
            self._emit_expr(code, node.expression)
            code.add_instr(POP)

        elif t is LetStatement:
            self._emit_expr(code, node.value)
            code.add_instr(DEFINE, code.add_name(node.name.value))

        elif t is AssignStatement:
            self._emit_expr(code, node.value)
            code.add_instr(DUP)
            code.add_instr(STORE, code.add_name(node.name))

        elif t is ReturnStatement:
            if node.value:
                self._emit_expr(code, node.value)
            else:
                code.add_instr(PUSH_NIL)
            code.add_instr(RET)

        elif t is BlockStatement:
            for s in node.statements:
                self._emit_stmt(code, s)

        elif t is LoopExpression:
            self._emit_loop(code, node)

        elif t is IfExpression:
            self._emit_if_stmt(code, node)

        else:
            raise CompilerError(f"unknown statement: {t.__name__}")

    # ----- Expression dispatch -----

    def _emit_expr(self, code, node):
        t = type(node)

        if t is Identifier:
            name = node.value
            if name in self._builtin_names:
                code.add_instr(BUILTIN, code.add_builtin(name))
            else:
                code.add_instr(LOAD, code.add_name(name))

        elif t is NumberLiteral:
            val = node.value
            if isinstance(val, int):
                code.add_instr(PUSH_INT, code.add_const(val))
            else:
                code.add_instr(PUSH_FLOAT, code.add_const(val))

        elif t is StringLiteral:
            code.add_instr(PUSH_STR, code.add_const(node.value))

        elif t is BooleanLiteral:
            code.add_instr(PUSH_TRUE if node.value else PUSH_FALSE)

        elif t is NilLiteral:
            code.add_instr(PUSH_NIL)

        elif t is ArrayLiteral:
            for el in node.elements:
                self._emit_expr(code, el)
            code.add_instr(MKARR, len(node.elements))

        elif t is MapLiteral:
            for k, v in node.pairs.items():
                self._emit_expr(code, k)
                self._emit_expr(code, v)
            code.add_instr(MKOBJ, len(node.pairs))

        elif t is PrefixExpression:
            self._emit_expr(code, node.right)
            if node.operator == '-':
                code.add_instr(NEG)
            elif node.operator == '+':
                code.add_instr(POS)
            elif node.operator in ('not', '!'):
                code.add_instr(NOT)
            else:
                raise CompilerError(f"unknown prefix: '{node.operator}'")

        elif t is InfixExpression:
            self._emit_infix(code, node)

        elif t is IfExpression:
            self._emit_expr(code, node.condition)
            else_idx = code.add_instr(JIF, 0)
            self._emit_stmt(code, node.consequence)
            if node.alternative:
                end_idx = code.add_instr(JMP, 0)
                code.patch_jump(else_idx, len(code.instrs))
                self._emit_stmt(code, node.alternative)
                code.patch_jump(end_idx, len(code.instrs))
            else:
                code.add_instr(PUSH_NIL)  # if has no else, result is nil
                end_idx = code.add_instr(JMP, 0)
                code.patch_jump(else_idx, len(code.instrs))
                code.add_instr(POP)  # pop the condition result
                code.patch_jump(end_idx, len(code.instrs))

        elif t is FnLiteral:
            self._emit_fn(code, node)

        elif t is CallExpression:
            for arg in node.arguments:
                self._emit_expr(code, arg)
            self._emit_expr(code, node.function)
            code.add_instr(CALL, len(node.arguments))

        elif t is IndexExpression:
            self._emit_expr(code, node.left)
            self._emit_expr(code, node.index)
            code.add_instr(INDEX)

        else:
            raise CompilerError(f"unknown expression: {t.__name__}")

    # ----- Infix (binary operators) -----

    def _emit_infix(self, code, node):
        op = node.operator

        # Assignment
        if op == '=':
            if not isinstance(node.left, Identifier):
                raise CompilerError("left side of = must be an identifier")
            self._emit_expr(code, node.right)
            code.add_instr(DUP)
            code.add_instr(STORE, code.add_name(node.left.value))
            return

        # Short-circuit logical operators
        if op == 'and':
            self._emit_expr(code, node.left)
            skip_idx = code.add_instr(JIF, 0)
            code.add_instr(POP)
            self._emit_expr(code, node.right)
            code.patch_jump(skip_idx, len(code.instrs))
            return

        if op == 'or':
            self._emit_expr(code, node.left)
            skip_idx = code.add_instr(JIF, 0)  # if truthy, skip right
            code.add_instr(POP)
            self._emit_expr(code, node.right)
            code.patch_jump(skip_idx, len(code.instrs))
            return

        # Normal binary
        self._emit_expr(code, node.left)
        self._emit_expr(code, node.right)

        _OP_MAP = {
            '+': ADD, '-': SUB, '*': MUL, '/': DIV, '%': MOD,
            '==': EQ, '!=': NE,
            '<': LT, '>': GT, '<=': LE, '>=': GE,
        }
        bc = _OP_MAP.get(op)
        if bc is None:
            raise CompilerError(f"unknown operator '{op}'")
        code.add_instr(bc)

    # ----- Loop -----

    def _emit_loop(self, code, node):
        if node.is_while:
            # loop condition { body }
            start = len(code.instrs)
            self._emit_expr(code, node.iterable)
            jif_idx = code.add_instr(JIF, 0)
            self._emit_stmt(code, node.body)
            code.add_instr(JMP, start)
            code.patch_jump(jif_idx, len(code.instrs))
        else:
            # for x in iterable { body }
            # Desugar:
            #   _it = iterable
            #   _i = 0
            #   _l = len(_it)
            #   loop _i < _l {
            #       x = _it[_i]
            #       body
            #       _i = _i + 1
            #   }
            it_name = self._temp_name()
            i_name = self._temp_name()
            ln_name = self._temp_name()

            self._emit_expr(code, node.iterable)
            code.add_instr(DEFINE, code.add_name(it_name))

            code.add_instr(PUSH_INT, code.add_const(0))
            code.add_instr(DEFINE, code.add_name(i_name))

            code.add_instr(LOAD, code.add_name(it_name))
            code.add_instr(LEN)
            code.add_instr(DEFINE, code.add_name(ln_name))

            # Loop header
            loop_start = len(code.instrs)
            code.add_instr(LOAD, code.add_name(i_name))
            code.add_instr(LOAD, code.add_name(ln_name))
            code.add_instr(LT)
            jif_idx = code.add_instr(JIF, 0)

            # Body: x = _it[_i]
            code.add_instr(LOAD, code.add_name(it_name))
            code.add_instr(LOAD, code.add_name(i_name))
            code.add_instr(INDEX)
            code.add_instr(DEFINE, code.add_name(node.identifier))

            self._emit_stmt(code, node.body)

            # i = i + 1
            code.add_instr(LOAD, code.add_name(i_name))
            code.add_instr(PUSH_INT, code.add_const(1))
            code.add_instr(ADD)
            code.add_instr(DUP)
            code.add_instr(STORE, code.add_name(i_name))
            code.add_instr(POP)  # discard dup

            code.add_instr(JMP, loop_start)
            code.patch_jump(jif_idx, len(code.instrs))

    # ----- If statement (no result needed) -----

    def _emit_if_stmt(self, code, node):
        """Emit if as statement (no stack value needed)."""
        self._emit_expr(code, node.condition)
        else_idx = code.add_instr(JIF, 0)
        self._emit_stmt(code, node.consequence)
        if node.alternative:
            end_idx = code.add_instr(JMP, 0)
            code.patch_jump(else_idx, len(code.instrs))
            self._emit_stmt(code, node.alternative)
            code.patch_jump(end_idx, len(code.instrs))
        else:
            code.patch_jump(else_idx, len(code.instrs))

    # ----- Function literal -----

    def _emit_fn(self, code, node):
        fn_code = CodeObject("<lambda>", len(node.parameters))
        for p in node.parameters:
            fn_code.add_name(p.value)

        stmts = node.body.statements
        for i, s in enumerate(stmts):
            is_last = (i == len(stmts) - 1)
            if is_last and isinstance(s, ExpressionStatement):
                # Last expression in function body = implicit return
                self._emit_expr(fn_code, s.expression)
            else:
                self._emit_stmt(fn_code, s)

        # If the last statement was an expression, we don't need implicit nil
        # Otherwise, implicit nil return
        if stmts and isinstance(stmts[-1], ExpressionStatement):
            fn_code.add_instr(RET)  # already has the expression value on stack
        else:
            fn_code.add_instr(PUSH_NIL)
            fn_code.add_instr(RET)

        idx = code.add_fn_obj(fn_code)
        code.add_instr(MKFN, idx)


def compile_program(program):
    """Compile a program to bytecode."""
    code = Compiler().compile(program)
    _peephole(code)
    return code


# ---------------------------------------------------------------------------
# Peephole optimizer — removes dead instructions, adjusts jump targets
# ---------------------------------------------------------------------------

def _peephole(code):
    _opt_code(code)
    for fn in code.fn_objects:
        _peephole(fn)


def _opt_code(code):
    instrs = code.instrs
    if not instrs:
        return

    # Collect all jump targets
    targets = set()
    for ins in instrs:
        if ins.op in (JMP, JIF) and ins.arg is not None:
            targets.add(ins.arg)

    # Build new instruction list
    new_ins = []
    i = 0
    n = len(instrs)
    # Map old index -> new index
    old_to_new = list(range(n))  # start with identity
    removed = 0

    while i < n:
        ins = instrs[i]

        # DUP ; STORE x ; POP → STORE x ; POP (remove DUP)
        if (i + 2 < n
                and ins.op == DUP
                and instrs[i+1].op == STORE
                and instrs[i+2].op == POP):
            # Keep STORE and POP, skip DUP
            new_ins.append(instrs[i+1])
            new_ins.append(instrs[i+2])
            old_to_new[i] = len(new_ins) - 2  # not used, but mark
            old_to_new[i+1] = len(new_ins) - 2
            old_to_new[i+2] = len(new_ins) - 1
            i += 3
            continue

        # PUSH_*; POP → remove both
        if (i + 1 < n
                and ins.op in (PUSH_NIL, PUSH_TRUE, PUSH_FALSE, PUSH_INT, PUSH_FLOAT, PUSH_STR)
                and instrs[i+1].op == POP
                and i not in targets            # Don't remove if jumped to
                and i + 1 not in targets):      # Don't remove if jumped to
            old_to_new[i] = len(new_ins)
            old_to_new[i+1] = len(new_ins)
            i += 2
            continue

        new_ins.append(ins)
        old_to_new[i] = len(new_ins) - 1
        i += 1

    if len(new_ins) == n:
        return  # no changes

    # Update jump targets using the mapping
    for ins in new_ins:
        if ins.op in (JMP, JIF) and ins.arg is not None:
            old_target = ins.arg
            # The new target is whatever new_ins index old_target maps to
            # old_to_new[old_target] = new index where that instruction ended up
            new_target = old_to_new[old_target]
            ins.arg = new_target

    code.instrs = new_ins
