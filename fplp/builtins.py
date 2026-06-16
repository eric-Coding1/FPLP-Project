"""FPLP Language - Built-in Functions"""

import time
import random
import math
import os as _os


# --- Error / Return types ---


# --- Error / Return types ---

class FPLPError(Exception):
    """Runtime error."""
    def __init__(self, message):
        self.message = message
        super().__init__(message)

    def __str__(self):
        return f"Error: {self.message}"


class ReturnValue:
    """Wraps a return value for flow control."""
    def __init__(self, value):
        self.value = value


class BreakSignal:
    """Signals a `break` from a loop."""
    pass


class ContinueSignal:
    """Signals a `continue` from a loop."""
    pass


class BuiltinFunction:
    def __init__(self, name, fn, min_args=0, max_args=None):
        self.name = name
        self.fn = fn
        self.min_args = min_args
        self.max_args = max_args

    def call(self, args):
        if len(args) < self.min_args:
            raise FPLPError(
                f"'{self.name}' requires at least {self.min_args} argument(s), "
                f"got {len(args)}"
            )
        if self.max_args is not None and len(args) > self.max_args:
            raise FPLPError(
                f"'{self.name}' accepts at most {self.max_args} argument(s), "
                f"got {len(args)}"
            )
        return self.fn(args)

    def __str__(self):
        return f"<builtin fn {self.name}>"

    def __repr__(self):
        return self.__str__()


# --- Implementations ---

def _print(args):
    """print(...) - output to stdout"""
    parts = []
    for a in args:
        if a is None:
            parts.append("nil")
        elif isinstance(a, bool):
            parts.append("true" if a else "false")
        else:
            parts.append(str(a))
    print(' '.join(parts))
    return None


def _println(args):
    """println(...) - output with newline (same as print but adds trailing newline via print's default)"""
    _print(args)
    return None


def _len(args):
    """len(x) - get length of string, array, or map"""
    val = args[0]
    if isinstance(val, str):
        return len(val)
    if isinstance(val, list):
        return len(val)
    if isinstance(val, dict):
        return len(val)
    raise FPLPError(f"len() not supported for {type(val).__name__}")


def _type(args):
    """type(x) - get type name as string"""
    val = args[0]
    if val is None:
        return "nil"
    if isinstance(val, bool):
        return "bool"
    if isinstance(val, int):
        return "int"
    if isinstance(val, float):
        return "float"
    if isinstance(val, str):
        return "string"
    if isinstance(val, list):
        return "array"
    if isinstance(val, dict):
        return "map"
    if isinstance(val, tuple):  # Function (fn literal stored as tuple)
        return "function"
    return "unknown"


def _int_(args):
    """int(x) - convert to integer"""
    val = args[0]
    if isinstance(val, int):
        return val
    if isinstance(val, float):
        return int(val)
    if isinstance(val, str):
        try:
            return int(val)
        except ValueError:
            raise FPLPError(f"cannot convert '{val}' to int")
    raise FPLPError(f"cannot convert {type(val).__name__} to int")


def _float_(args):
    """float(x) - convert to float"""
    val = args[0]
    if isinstance(val, (int, float)):
        return float(val)
    if isinstance(val, str):
        try:
            return float(val)
        except ValueError:
            raise FPLPError(f"cannot convert '{val}' to float")
    raise FPLPError(f"cannot convert {type(val).__name__} to float")


def _str_(args):
    """str(x) - convert to string"""
    val = args[0]
    if val is None:
        return "nil"
    if isinstance(val, bool):
        return "true" if val else "false"
    return str(val)


def _range(args):
    """range(end) or range(start, end) or range(start, end, step)"""
    if len(args) == 1:
        start, end, step = 0, args[0], 1
    elif len(args) == 2:
        start, end, step = args[0], args[1], 1
    elif len(args) == 3:
        start, end, step = args[0], args[1], args[2]
    else:
        raise FPLPError("range() accepts 1-3 arguments")

    if not all(isinstance(x, (int, float)) for x in [start, end, step]):
        raise FPLPError("range() arguments must be numbers")

    result = []
    i = start
    if step > 0:
        while i < end:
            result.append(i)
            i += step
    else:
        while i > end:
            result.append(i)
            i += step
    return result


def _input(args):
    """input(prompt) - read a line from stdin"""
    prompt = args[0] if args else ""
    try:
        return input(prompt)
    except EOFError:
        return ""


def _push(args):
    """push(arr, val) - add element to end of array (mutates)"""
    arr = args[0]
    val = args[1]
    if not isinstance(arr, list):
        raise FPLPError("push() first argument must be an array")
    arr.append(val)
    return arr


def _pop(args):
    """pop(arr) - remove and return last element"""
    arr = args[0]
    if not isinstance(arr, list):
        raise FPLPError("pop() argument must be an array")
    if len(arr) == 0:
        return None
    return arr.pop()


def _keys(args):
    """keys(map) - return list of map keys"""
    m = args[0]
    if not isinstance(m, dict):
        raise FPLPError("keys() argument must be a map")
    return list(m.keys())


def _values(args):
    """values(map) - return list of map values"""
    m = args[0]
    if not isinstance(m, dict):
        raise FPLPError("values() argument must be a map")
    return list(m.values())


def _sleep(args):
    """sleep(seconds) - pause execution"""
    secs = args[0]
    if not isinstance(secs, (int, float)):
        raise FPLPError("sleep() argument must be a number")
    time.sleep(secs)
    return None


def _rand(args):
    """rand() or rand(max) or rand(min, max) - random number"""
    if len(args) == 0:
        return random.random()
    if len(args) == 1:
        return random.randint(0, args[0])
    return random.randint(args[0], args[1])


# ===== NEW: String Functions =====

def _split(args):
    """split(str, sep) - split string by separator"""
    s, sep = str(args[0]), str(args[1])
    return s.split(sep) if sep else list(s)


def _join(args):
    """join(arr, sep) - join array of strings"""
    arr, sep = args[0], str(args[1]) if len(args) > 1 else ""
    if not isinstance(arr, list):
        raise FPLPError("join() first argument must be an array")
    return sep.join(str(x) for x in arr)


def _str_replace(args):
    """str_replace(str, old, new)"""
    s, old, new = str(args[0]), str(args[1]), str(args[2])
    return s.replace(old, new)


def _upper(args):
    """upper(str)"""
    return str(args[0]).upper()


def _lower(args):
    """lower(str)"""
    return str(args[0]).lower()


def _trim(args):
    """trim(str)"""
    return str(args[0]).strip()


def _contains(args):
    """contains(str, substr)"""
    return str(args[1]) in str(args[0])


def _starts_with(args):
    """starts_with(str, prefix)"""
    return str(args[0]).startswith(str(args[1]))


def _ends_with(args):
    """ends_with(str, suffix)"""
    return str(args[0]).endswith(str(args[1]))


# ===== NEW: Math Functions =====

def _abs(args):
    return abs(args[0])


def _min_(args):
    return min(args)


def _max_(args):
    return max(args)


def _sqrt(args):
    return math.sqrt(args[0])


def _floor(args):
    return math.floor(args[0])


def _ceil(args):
    return math.ceil(args[0])


def _round_(args):
    return round(args[0])


def _sin(args):
    return math.sin(args[0])


def _cos(args):
    return math.cos(args[0])


def _pow(args):
    return args[0] ** args[1]


# ===== NEW: File IO Functions =====

def _read_file(args):
    """read_file(path) - read file content as string"""
    path = args[0]
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise FPLPError(f"cannot read file '{path}': {e}")


def _write_file(args):
    """write_file(path, content) - write string to file"""
    path, content = args[0], str(args[1])
    try:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise FPLPError(f"cannot write file '{path}': {e}")
    return None


def _append_file(args):
    """append_file(path, content) - append string to file"""
    path, content = args[0], str(args[1])
    try:
        with open(path, 'a', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        raise FPLPError(f"cannot append to file '{path}': {e}")
    return None


# ===== NEW: Array/List Utilities =====

def _reverse(args):
    """reverse(arr) - reverse array (returns new copy)"""
    arr = args[0]
    if not isinstance(arr, list):
        raise FPLPError("reverse() argument must be an array")
    return list(reversed(arr))


def _sort_(args):
    """sort(arr) - sort array (mutates)"""
    arr = args[0]
    if not isinstance(arr, list):
        raise FPLPError("sort() argument must be an array")
    arr.sort()
    return arr


def _slice_(args):
    """slice(arr, start, end) - slice array"""
    arr = args[0]
    start = int(args[1]) if len(args) > 1 else 0
    end = int(args[2]) if len(args) > 2 else len(arr)
    if not isinstance(arr, list):
        raise FPLPError("slice() first argument must be an array")
    return arr[start:end]


# --- Registry ---

BUILTINS = {
    "print": BuiltinFunction("print", _print, min_args=0),
    "println": BuiltinFunction("println", _println, min_args=0),
    "len": BuiltinFunction("len", _len, min_args=1, max_args=1),
    "type": BuiltinFunction("type", _type, min_args=1, max_args=1),
    "int": BuiltinFunction("int", _int_, min_args=1, max_args=1),
    "float": BuiltinFunction("float", _float_, min_args=1, max_args=1),
    "str": BuiltinFunction("str", _str_, min_args=1, max_args=1),
    "range": BuiltinFunction("range", _range, min_args=1, max_args=3),
    "input": BuiltinFunction("input", _input, min_args=0, max_args=1),
    "push": BuiltinFunction("push", _push, min_args=2, max_args=2),
    "pop": BuiltinFunction("pop", _pop, min_args=1, max_args=1),
    "keys": BuiltinFunction("keys", _keys, min_args=1, max_args=1),
    "values": BuiltinFunction("values", _values, min_args=1, max_args=1),
    "sleep": BuiltinFunction("sleep", _sleep, min_args=1, max_args=1),
    "rand": BuiltinFunction("rand", _rand, min_args=0, max_args=2),
    # String functions
    "split": BuiltinFunction("split", _split, min_args=2, max_args=2),
    "join": BuiltinFunction("join", _join, min_args=1, max_args=2),
    "str_replace": BuiltinFunction("str_replace", _str_replace, min_args=3, max_args=3),
    "upper": BuiltinFunction("upper", _upper, min_args=1, max_args=1),
    "lower": BuiltinFunction("lower", _lower, min_args=1, max_args=1),
    "trim": BuiltinFunction("trim", _trim, min_args=1, max_args=1),
    "contains": BuiltinFunction("contains", _contains, min_args=2, max_args=2),
    "starts_with": BuiltinFunction("starts_with", _starts_with, min_args=2, max_args=2),
    "ends_with": BuiltinFunction("ends_with", _ends_with, min_args=2, max_args=2),
    # Math functions
    "abs": BuiltinFunction("abs", _abs, min_args=1, max_args=1),
    "min": BuiltinFunction("min", _min_, min_args=1),
    "max": BuiltinFunction("max", _max_, min_args=1),
    "sqrt": BuiltinFunction("sqrt", _sqrt, min_args=1, max_args=1),
    "floor": BuiltinFunction("floor", _floor, min_args=1, max_args=1),
    "ceil": BuiltinFunction("ceil", _ceil, min_args=1, max_args=1),
    "round": BuiltinFunction("round", _round_, min_args=1, max_args=1),
    "sin": BuiltinFunction("sin", _sin, min_args=1, max_args=1),
    "cos": BuiltinFunction("cos", _cos, min_args=1, max_args=1),
    "pow": BuiltinFunction("pow", _pow, min_args=2, max_args=2),
    # File IO
    "read_file": BuiltinFunction("read_file", _read_file, min_args=1, max_args=1),
    "write_file": BuiltinFunction("write_file", _write_file, min_args=2, max_args=2),
    "append_file": BuiltinFunction("append_file", _append_file, min_args=2, max_args=2),
    # Array utilities
    "reverse": BuiltinFunction("reverse", _reverse, min_args=1, max_args=1),
    "sort": BuiltinFunction("sort", _sort_, min_args=1, max_args=1),
    "slice": BuiltinFunction("slice", _slice_, min_args=1, max_args=3),
}

# Merge graphics functions (lazy import to avoid circular deps)
try:
    from .graphics import GRAPHICS_FUNCS
    BUILTINS.update(GRAPHICS_FUNCS)
except ImportError:
    pass  # graphics module not available

# Merge extension libraries (json, math, os, string, time)
try:
    from .libs import LIBS
    BUILTINS.update(LIBS)
except ImportError:
    pass  # libs module not available
