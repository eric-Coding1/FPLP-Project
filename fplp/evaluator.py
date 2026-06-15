"""FPLP Language - Tree-walking Evaluator"""

from .ast_nodes import *
from .environment import Environment
from .builtins import BUILTINS, FPLPError, ReturnValue, BuiltinFunction


class Function:
    """User-defined function: fn literal + closure environment."""
    def __init__(self, literal, env):
        self.literal = literal    # FnLiteral AST node
        self.env = env            # captured environment (closure)

    def __str__(self):
        return str(self.literal)

    def __repr__(self):
        return self.__str__()


def is_truthy(val):
    """Check if value is truthy."""
    if val is None:
        return False
    if isinstance(val, bool):
        return val
    if isinstance(val, (int, float)):
        return val != 0
    if isinstance(val, str):
        return len(val) > 0
    if isinstance(val, (list, dict)):
        return len(val) > 0
    return True


def eval_program(program, env):
    """Evaluate a program, returning the last expression value if any."""
    result = None
    for stmt in program.statements:
        result = eval_node(stmt, env)
        if isinstance(result, ReturnValue):
            return result.value
        if isinstance(result, FPLPError):
            return result
    return result


def eval_block(block, env):
    """Evaluate a block, creating a new scope."""
    new_env = Environment(env)
    result = None
    for stmt in block.statements:
        result = eval_node(stmt, new_env)
        if isinstance(result, (ReturnValue, FPLPError)):
            return result
    return result


def eval_node(node, env):
    """Main evaluation dispatcher."""
    if node is None:
        return None

    # --- Statements ---

    if isinstance(node, Program):
        return eval_program(node, env)

    if isinstance(node, ExpressionStatement):
        return eval_node(node.expression, env)

    if isinstance(node, LetStatement):
        value = eval_node(node.value, env)
        if isinstance(value, FPLPError):
            return value
        env.set(node.name.value, value)
        return None

    if isinstance(node, AssignStatement):
        value = eval_node(node.value, env)
        if isinstance(value, FPLPError):
            return value
        if not env.assign(node.name, value):
            raise FPLPError(f"undefined variable '{node.name}'")
        return value

    if isinstance(node, ReturnStatement):
        value = eval_node(node.value, env)
        if isinstance(value, FPLPError):
            return value
        return ReturnValue(value)

    if isinstance(node, BlockStatement):
        return eval_block(node, env)

    if isinstance(node, LoopExpression):
        return _eval_loop(node, env)

    # --- Expressions ---

    if isinstance(node, Identifier):
        return _eval_identifier(node, env)

    if isinstance(node, NumberLiteral):
        return node.value

    if isinstance(node, StringLiteral):
        return node.value

    if isinstance(node, BooleanLiteral):
        return node.value

    if isinstance(node, NilLiteral):
        return None

    if isinstance(node, ArrayLiteral):
        elements = []
        for el in node.elements:
            val = eval_node(el, env)
            if isinstance(val, FPLPError):
                return val
            elements.append(val)
        return elements

    if isinstance(node, MapLiteral):
        pairs = {}
        for key_node, val_node in node.pairs.items():
            key = eval_node(key_node, env)
            if isinstance(key, FPLPError):
                return key
            val = eval_node(val_node, env)
            if isinstance(val, FPLPError):
                return val
            pairs[key] = val
        return pairs

    if isinstance(node, PrefixExpression):
        return _eval_prefix(node, env)

    if isinstance(node, InfixExpression):
        return _eval_infix(node, env)

    if isinstance(node, IfExpression):
        return _eval_if(node, env)

    if isinstance(node, FnLiteral):
        return Function(node, env)

    if isinstance(node, CallExpression):
        return _eval_call(node, env)

    if isinstance(node, IndexExpression):
        return _eval_index(node, env)

    raise FPLPError(f"unknown AST node type: {type(node).__name__}")


def _eval_identifier(node, env):
    name = node.value
    # Check local scope
    val = env.get(name)
    if val is not None:
        return val
    # Check builtins
    if name in BUILTINS:
        return BUILTINS[name]
    raise FPLPError(f"undefined variable '{name}'")


def _eval_prefix(node, env):
    op = node.operator
    right = eval_node(node.right, env)
    if isinstance(right, FPLPError):
        return right

    if op == '-':
        if isinstance(right, (int, float)):
            return -right
        raise FPLPError(f"cannot negate {type(right).__name__}")

    if op == '+':
        if isinstance(right, (int, float)):
            return +right
        raise FPLPError(f"cannot apply + to {type(right).__name__}")

    if op == 'not':
        return not is_truthy(right)

    if op == '!':
        return not is_truthy(right)

    raise FPLPError(f"unknown prefix operator '{op}'")


def _eval_infix(node, env):
    op = node.operator

    # Assignment operator: don't evaluate left side, just get the variable name
    if op == '=':
        if not isinstance(node.left, Identifier) and not (hasattr(node.left, 'value')):
            raise FPLPError("Left side of assignment must be an identifier")
        name = node.left.value if hasattr(node.left, 'value') else str(node.left)
        right = eval_node(node.right, env)
        if isinstance(right, FPLPError):
            return right
        if not env.assign(name, right):
            raise FPLPError(f"undefined variable '{name}'")
        return right

    left = eval_node(node.left, env)
    if isinstance(left, FPLPError):
        return left
    right = eval_node(node.right, env)
    if isinstance(right, FPLPError):
        return right

    # String concatenation with +
    if op == '+' and isinstance(left, str) and isinstance(right, str):
        return left + right

    # String * number repetition
    if op == '*' and isinstance(left, str) and isinstance(right, (int, float)):
        return left * int(right)
    if op == '*' and isinstance(left, (int, float)) and isinstance(right, str):
        return right * int(left)

    # Numeric operations
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if op == '+':
            return left + right
        if op == '-':
            return left - right
        if op == '*':
            return left * right
        if op == '/':
            if right == 0:
                raise FPLPError("division by zero")
            # Return float for division
            result = left / right
            return int(result) if result == int(result) and not isinstance(left, float) and not isinstance(right, float) else result
        if op == '%':
            if right == 0:
                raise FPLPError("modulo by zero")
            return left % right

    # Comparisons (works on numbers and strings)
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        if op == '<': return left < right
        if op == '>': return left > right
        if op == '<=': return left <= right
        if op == '>=': return left >= right

    # Equality (works on all types)
    if op == '==':
        return _deep_eq(left, right)
    if op == '!=':
        return not _deep_eq(left, right)

    # Logical operators
    if op == 'and':
        return is_truthy(left) and is_truthy(right)
    if op == 'or':
        return is_truthy(left) or is_truthy(right)

    # Comparison on other comparable types
    if op == '<': return left < right if _is_comparable(left, right) else False
    if op == '>': return left > right if _is_comparable(left, right) else False
    if op == '<=': return left <= right if _is_comparable(left, right) else False
    if op == '>=': return left >= right if _is_comparable(left, right) else False

    raise FPLPError(
        f"unsupported operator '{op}' for {type(left).__name__} and {type(right).__name__}"
    )


def _is_comparable(a, b):
    """Check if two types can be compared."""
    return type(a) == type(b) and isinstance(a, (str, int, float, bool))


def _deep_eq(a, b):
    """Deep equality comparison."""
    if type(a) != type(b):
        return False
    if isinstance(a, dict):
        if set(a.keys()) != set(b.keys()):
            return False
        return all(_deep_eq(a[k], b[k]) for k in a)
    if isinstance(a, list):
        if len(a) != len(b):
            return False
        return all(_deep_eq(x, y) for x, y in zip(a, b))
    return a == b


def _eval_if(node, env):
    condition = eval_node(node.condition, env)
    if isinstance(condition, FPLPError):
        return condition

    if is_truthy(condition):
        return eval_block(node.consequence, env)
    elif node.alternative is not None:
        return eval_block(node.alternative, env)

    return None


def _eval_loop(node, env):
    """Evaluate loop expressions."""
    if node.is_while:
        # While-loop: loop condition { body }
        result = None
        while True:
            condition = eval_node(node.iterable, env)
            if isinstance(condition, FPLPError):
                return condition
            if not is_truthy(condition):
                break
            result = eval_block(node.body, env)
            if isinstance(result, ReturnValue):
                return result
            if isinstance(result, FPLPError):
                return result
        return result
    else:
        # For-each loop: loop var in iterable { body }
        iterable = eval_node(node.iterable, env)
        if isinstance(iterable, FPLPError):
            return iterable

        if not isinstance(iterable, (list, str)):
            raise FPLPError(f"cannot iterate over {type(iterable).__name__}")

        result = None
        for item in iterable:
            # Create new scope for each iteration
            loop_env = Environment(env)
            loop_env.set(node.identifier, item)
            result = eval_block(node.body, loop_env)
            if isinstance(result, ReturnValue):
                return result
            if isinstance(result, FPLPError):
                return result

        return result


def _eval_call(node, env):
    """Evaluate function / method calls."""
    fn_val = eval_node(node.function, env)
    if isinstance(fn_val, FPLPError):
        return fn_val

    args = []
    for arg_node in node.arguments:
        arg_val = eval_node(arg_node, env)
        if isinstance(arg_val, FPLPError):
            return arg_val
        args.append(arg_val)

    # Built-in function
    if isinstance(fn_val, BuiltinFunction) or hasattr(fn_val, 'call'):
        return fn_val.call(args)

    # User-defined function
    if isinstance(fn_val, Function):
        fn = fn_val
        if len(args) != len(fn.literal.parameters):
            raise FPLPError(
                f"function expects {len(fn.literal.parameters)} argument(s), "
                f"got {len(args)}"
            )
        # Create new scope: closure env extended with parameters
        call_env = Environment(fn.env)
        for param, arg in zip(fn.literal.parameters, args):
            call_env.set(param.value, arg)

        result = eval_block(fn.literal.body, call_env)
        if isinstance(result, ReturnValue):
            return result.value
        return result

    raise FPLPError(f"'{fn_val}' is not callable")


def _eval_index(node, env):
    left = eval_node(node.left, env)
    if isinstance(left, FPLPError):
        return left

    index = eval_node(node.index, env)
    if isinstance(index, FPLPError):
        return index

    if isinstance(left, list):
        if not isinstance(index, int):
            raise FPLPError(f"list index must be int, got {type(index).__name__}")
        if index < 0 or index >= len(left):
            raise FPLPError(f"list index out of range: {index}")
        return left[index]

    if isinstance(left, str):
        if not isinstance(index, (int, str)):
            raise FPLPError(f"string index must be int or string, got {type(index).__name__}")
        if isinstance(index, int):
            if index < 0 or index >= len(left):
                raise FPLPError(f"string index out of range: {index}")
            return left[index]
        else:
            # Can't index string by string in FPLP
            raise FPLPError("string index must be int")

    if isinstance(left, dict):
        if index in left:
            return left[index]
        return None  # missing key returns nil

    raise FPLPError(f"cannot index {type(left).__name__}")
