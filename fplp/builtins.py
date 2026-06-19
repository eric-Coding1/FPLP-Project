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


# ===== NEW: Type Check Helpers =====

def _is_nil(args):
    return args[0] is None

def _is_bool(args):
    return isinstance(args[0], bool)

def _is_int(args):
    return isinstance(args[0], int) and not isinstance(args[0], bool)

def _is_float(args):
    return isinstance(args[0], float)

def _is_string(args):
    return isinstance(args[0], str)

def _is_array(args):
    return isinstance(args[0], list)

def _is_map(args):
    return isinstance(args[0], dict)

def _is_fn(args):
    from .vm import Closure
    val = args[0]
    return isinstance(val, (tuple, Closure)) or (hasattr(val, '__code__') and not hasattr(val, 'call'))


# ===== NEW: Assertion & Debug =====

def _assert(args):
    """assert(condition) or assert(condition, message)"""
    if not args[0]:
        msg = str(args[1]) if len(args) > 1 else "assertion failed"
        raise FPLPError(msg)
    return None

def _debug(args):
    """debug(x) - print value with type info"""
    val = args[0]
    type_name = "nil" if val is None else type(val).__name__
    print(f"[debug] ({type_name}) {val}")
    return val


# ===== NEW: Functional Programming =====

def _map_fn(args):
    """map(fn, arr) - apply fn to each element"""
    fn, arr = args[0], args[1]
    if not isinstance(arr, list):
        raise FPLPError("map() second argument must be an array")
    result = []
    for item in arr:
        result.append(fn(item))
    return result

def _filter_fn(args):
    """filter(fn, arr) - keep elements where fn returns truthy"""
    fn, arr = args[0], args[1]
    if not isinstance(arr, list):
        raise FPLPError("filter() second argument must be an array")
    result = []
    for item in arr:
        if fn(item):
            result.append(item)
    return result

def _reduce_fn(args):
    """reduce(fn, arr, initial) - accumulate"""
    fn, arr = args[0], args[1]
    if not isinstance(arr, list):
        raise FPLPError("reduce() second argument must be an array")
    if not arr:
        return args[2] if len(args) > 2 else None
    start = 1
    acc = arr[0]
    if len(args) > 2:
        acc = args[2]
        start = 0
    for i in range(start, len(arr)):
        acc = fn(acc, arr[i])
    return acc

def _all_fn(args):
    """all(arr) - true if all elements are truthy"""
    arr = args[0]
    if not isinstance(arr, list):
        raise FPLPError("all() argument must be an array")
    for item in arr:
        if not item:
            return False
    return True

def _any_fn(args):
    """any(arr) - true if any element is truthy"""
    arr = args[0]
    if not isinstance(arr, list):
        raise FPLPError("any() argument must be an array")
    for item in arr:
        if item:
            return True
    return False

def _sum_fn(args):
    """sum(arr) - sum of array elements"""
    arr = args[0]
    if not isinstance(arr, list):
        raise FPLPError("sum() argument must be an array")
    total = 0
    for item in arr:
        total += item
    return total

def _product_fn(args):
    """product(arr) - product of array elements"""
    arr = args[0]
    if not isinstance(arr, list):
        raise FPLPError("product() argument must be an array")
    total = 1
    for item in arr:
        total *= item
    return total

def _flatten_fn(args):
    """flatten(arr) - flatten nested arrays one level"""
    arr = args[0]
    if not isinstance(arr, list):
        raise FPLPError("flatten() argument must be an array")
    result = []
    for item in arr:
        if isinstance(item, list):
            result.extend(item)
        else:
            result.append(item)
    return result

def _zip_fn(args):
    """zip(a, b) - zip two arrays into array of pairs"""
    a, b = args[0], args[1]
    if not isinstance(a, list) or not isinstance(b, list):
        raise FPLPError("zip() arguments must be arrays")
    result = []
    n = min(len(a), len(b))
    for i in range(n):
        result.append([a[i], b[i]])
    return result

def _enumerate_fn(args):
    """enumerate(arr) - return [[index, value], ...]"""
    arr = args[0]
    if not isinstance(arr, list):
        raise FPLPError("enumerate() argument must be an array")
    result = []
    for i, item in enumerate(arr):
        result.append([i, item])
    return result


# ===== NEW: Char Code Conversion =====

def _chr_fn(args):
    """chr(n) - convert int to character"""
    return chr(int(args[0]))

def _ord_fn(args):
    """ord(c) - convert character to int"""
    s = str(args[0])
    if len(s) != 1:
        raise FPLPError("ord() requires a single character")
    return ord(s)


# ===== NEW: Number Formatting =====

def _hex_fn(args):
    """hex(n) - convert to hex string"""
    return hex(int(args[0]))

def _bin_fn(args):
    """bin(n) - convert to binary string"""
    return bin(int(args[0]))

def _oct_fn(args):
    """oct(n) - convert to octal string"""
    return oct(int(args[0]))

def _bool_fn(args):
    """bool(x) - convert to bool"""
    return bool(args[0])

def _sign_fn(args):
    """sign(x) - return -1, 0, or 1"""
    val = args[0]
    if val > 0: return 1
    if val < 0: return -1
    return 0

def _clamp_fn(args):
    """clamp(x, lo, hi) - clamp value between lo and hi"""
    x, lo, hi = args[0], args[1], args[2]
    if x < lo: return lo
    if x > hi: return hi
    return x

def _lerp_fn(args):
    """lerp(a, b, t) - linear interpolation"""
    a, b, t = args[0], args[1], args[2]
    return a + (b - a) * t


# ===== NEW: Misc Utilities =====

def _copy_fn(args):
    """copy(x) - shallow copy of array or map"""
    val = args[0]
    if isinstance(val, list):
        return list(val)
    if isinstance(val, dict):
        return dict(val)
    return val

def _id_fn(args):
    """id(x) - return memory identity (pointer)"""
    return id(args[0])

def _repeat_fn(args):
    """repeat(s, n) - repeat string n times"""
    s, n = str(args[0]), int(args[1])
    return s * n

def _random_fn(args):
    """random() or random(max) - random float"""
    if len(args) == 0:
        return random.random()
    return random.random() * float(args[0])


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
    # Type checks
    "is_nil": BuiltinFunction("is_nil", _is_nil, min_args=1, max_args=1),
    "is_bool": BuiltinFunction("is_bool", _is_bool, min_args=1, max_args=1),
    "is_int": BuiltinFunction("is_int", _is_int, min_args=1, max_args=1),
    "is_float": BuiltinFunction("is_float", _is_float, min_args=1, max_args=1),
    "is_string": BuiltinFunction("is_string", _is_string, min_args=1, max_args=1),
    "is_array": BuiltinFunction("is_array", _is_array, min_args=1, max_args=1),
    "is_map": BuiltinFunction("is_map", _is_map, min_args=1, max_args=1),
    "is_fn": BuiltinFunction("is_fn", _is_fn, min_args=1, max_args=1),
    # Assertion & debug
    "assert": BuiltinFunction("assert", _assert, min_args=1, max_args=2),
    "debug": BuiltinFunction("debug", _debug, min_args=1, max_args=1),
    # Functional
    "map": BuiltinFunction("map", _map_fn, min_args=2, max_args=2),
    "filter": BuiltinFunction("filter", _filter_fn, min_args=2, max_args=2),
    "reduce": BuiltinFunction("reduce", _reduce_fn, min_args=2, max_args=3),
    "all": BuiltinFunction("all", _all_fn, min_args=1, max_args=1),
    "any": BuiltinFunction("any", _any_fn, min_args=1, max_args=1),
    "sum": BuiltinFunction("sum", _sum_fn, min_args=1, max_args=1),
    "product": BuiltinFunction("product", _product_fn, min_args=1, max_args=1),
    "flatten": BuiltinFunction("flatten", _flatten_fn, min_args=1, max_args=1),
    "zip": BuiltinFunction("zip", _zip_fn, min_args=2, max_args=2),
    "enumerate": BuiltinFunction("enumerate", _enumerate_fn, min_args=1, max_args=1),
    # Char code
    "chr": BuiltinFunction("chr", _chr_fn, min_args=1, max_args=1),
    "ord": BuiltinFunction("ord", _ord_fn, min_args=1, max_args=1),
    # Number formatting
    "hex": BuiltinFunction("hex", _hex_fn, min_args=1, max_args=1),
    "bin": BuiltinFunction("bin", _bin_fn, min_args=1, max_args=1),
    "oct": BuiltinFunction("oct", _oct_fn, min_args=1, max_args=1),
    "bool": BuiltinFunction("bool", _bool_fn, min_args=1, max_args=1),
    "sign": BuiltinFunction("sign", _sign_fn, min_args=1, max_args=1),
    "clamp": BuiltinFunction("clamp", _clamp_fn, min_args=3, max_args=3),
    "lerp": BuiltinFunction("lerp", _lerp_fn, min_args=3, max_args=3),
    # Misc
    "copy": BuiltinFunction("copy", _copy_fn, min_args=1, max_args=1),
    "id": BuiltinFunction("id", _id_fn, min_args=1, max_args=1),
    "repeat": BuiltinFunction("repeat", _repeat_fn, min_args=2, max_args=2),
    "random": BuiltinFunction("random", _random_fn, min_args=0, max_args=1),
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
