"""FPLP Language - Extension Libraries (json, math, os, string, time)"""

import json as _json
import math as _math
import os as _os
import time as _time
import datetime

from .builtins import BuiltinFunction, FPLPError


# ---------------------------------------------------------------------------
# json
# ---------------------------------------------------------------------------

def _json_parse(args):
    try:
        return _json.loads(str(args[0]))
    except _json.JSONDecodeError as e:
        raise FPLPError(f"json.parse error: {e}")

def _json_stringify(args):
    val = args[0]
    indent = args[1] if len(args) > 1 else None
    try:
        if indent is not None:
            return _json.dumps(val, indent=int(indent), ensure_ascii=False)
        return _json.dumps(val, ensure_ascii=False)
    except (TypeError, ValueError) as e:
        raise FPLPError(f"json.stringify error: {e}")

LIB_JSON = {
    "parse": BuiltinFunction("json.parse", _json_parse, min_args=1, max_args=1),
    "stringify": BuiltinFunction("json.stringify", _json_stringify, min_args=1, max_args=2),
}


# ---------------------------------------------------------------------------
# math (extensions beyond basic builtins)
# ---------------------------------------------------------------------------

def _math_log(args):
    x = args[0]
    base = args[1] if len(args) > 1 else _math.e
    return _math.log(x, base)

def _math_log10(args):
    return _math.log10(args[0])

def _math_exp(args):
    return _math.exp(args[0])

def _math_tan(args):
    return _math.tan(args[0])

def _math_asin(args):
    return _math.asin(args[0])

def _math_acos(args):
    return _math.acos(args[0])

def _math_atan(args):
    return _math.atan(args[0])

def _math_atan2(args):
    return _math.atan2(args[0], args[1])

def _math_radians(args):
    return _math.radians(args[0])

def _math_degrees(args):
    return _math.degrees(args[0])

def _math_isnan(args):
    return _math.isnan(args[0])

def _math_isinf(args):
    return _math.isinf(args[0])

def _math_gcd(args):
    return _math.gcd(args[0], args[1])

def _math_factorial(args):
    return _math.factorial(args[0])

def _math_sqrt(args):
    return _math.sqrt(args[0])

def _math_sin(args):
    return _math.sin(args[0])

def _math_cos(args):
    return _math.cos(args[0])

LIB_MATH = {
    "e": _math.e,
    "pi": _math.pi,
    "inf": float('inf'),
    "nan": float('nan'),
    "sqrt": BuiltinFunction("math.sqrt", _math_sqrt, min_args=1, max_args=1),
    "sin": BuiltinFunction("math.sin", _math_sin, min_args=1, max_args=1),
    "cos": BuiltinFunction("math.cos", _math_cos, min_args=1, max_args=1),
    "log": BuiltinFunction("math.log", _math_log, min_args=1, max_args=2),
    "log10": BuiltinFunction("math.log10", _math_log10, min_args=1, max_args=1),
    "exp": BuiltinFunction("math.exp", _math_exp, min_args=1, max_args=1),
    "tan": BuiltinFunction("math.tan", _math_tan, min_args=1, max_args=1),
    "asin": BuiltinFunction("math.asin", _math_asin, min_args=1, max_args=1),
    "acos": BuiltinFunction("math.acos", _math_acos, min_args=1, max_args=1),
    "atan": BuiltinFunction("math.atan", _math_atan, min_args=1, max_args=1),
    "atan2": BuiltinFunction("math.atan2", _math_atan2, min_args=2, max_args=2),
    "radians": BuiltinFunction("math.radians", _math_radians, min_args=1, max_args=1),
    "degrees": BuiltinFunction("math.degrees", _math_degrees, min_args=1, max_args=1),
    "isnan": BuiltinFunction("math.isnan", _math_isnan, min_args=1, max_args=1),
    "isinf": BuiltinFunction("math.isinf", _math_isinf, min_args=1, max_args=1),
    "gcd": BuiltinFunction("math.gcd", _math_gcd, min_args=2, max_args=2),
    "factorial": BuiltinFunction("math.factorial", _math_factorial, min_args=1, max_args=1),
}


# ---------------------------------------------------------------------------
# os
# ---------------------------------------------------------------------------

def _os_getenv(args):
    return _os.environ.get(str(args[0]), None)

def _os_setenv(args):
    _os.environ[str(args[0])] = str(args[1])
    return None

def _os_cwd(args):
    return _os.getcwd()

def _os_chdir(args):
    _os.chdir(str(args[0]))
    return None

def _os_listdir(args):
    path = str(args[0]) if args else "."
    try:
        return _os.listdir(path)
    except FileNotFoundError:
        raise FPLPError(f"directory not found: {path}")

def _os_mkdir(args):
    try:
        _os.mkdir(str(args[0]))
    except FileExistsError:
        raise FPLPError(f"directory already exists: {args[0]}")
    return None

def _os_remove(args):
    try:
        _os.remove(str(args[0]))
    except FileNotFoundError:
        raise FPLPError(f"file not found: {args[0]}")
    return None

def _os_exists(args):
    return _os.path.exists(str(args[0]))

def _os_isfile(args):
    return _os.path.isfile(str(args[0]))

def _os_isdir(args):
    return _os.path.isdir(str(args[0]))

def _os_rename(args):
    try:
        _os.rename(str(args[0]), str(args[1]))
    except FileNotFoundError:
        raise FPLPError(f"file not found: {args[0]}")
    return None

def _os_system(args):
    return _os.system(str(args[0]))

LIB_OS = {
    "getenv": BuiltinFunction("os.getenv", _os_getenv, min_args=1, max_args=1),
    "setenv": BuiltinFunction("os.setenv", _os_setenv, min_args=2, max_args=2),
    "cwd": BuiltinFunction("os.cwd", _os_cwd, min_args=0, max_args=0),
    "chdir": BuiltinFunction("os.chdir", _os_chdir, min_args=1, max_args=1),
    "listdir": BuiltinFunction("os.listdir", _os_listdir, min_args=0, max_args=1),
    "mkdir": BuiltinFunction("os.mkdir", _os_mkdir, min_args=1, max_args=1),
    "remove": BuiltinFunction("os.remove", _os_remove, min_args=1, max_args=1),
    "exists": BuiltinFunction("os.exists", _os_exists, min_args=1, max_args=1),
    "isfile": BuiltinFunction("os.isfile", _os_isfile, min_args=1, max_args=1),
    "isdir": BuiltinFunction("os.isdir", _os_isdir, min_args=1, max_args=1),
    "rename": BuiltinFunction("os.rename", _os_rename, min_args=2, max_args=2),
    "system": BuiltinFunction("os.system", _os_system, min_args=1, max_args=1),
}


# ---------------------------------------------------------------------------
# string
# ---------------------------------------------------------------------------

def _str_repeat(args):
    return str(args[0]) * int(args[1])

def _str_reverse(args):
    return str(args[0])[::-1]

def _str_pad_left(args):
    s = str(args[0])
    n = int(args[1])
    c = str(args[2]) if len(args) > 2 else " "
    return s.rjust(n, c)

def _str_pad_right(args):
    s = str(args[0])
    n = int(args[1])
    c = str(args[2]) if len(args) > 2 else " "
    return s.ljust(n, c)

def _str_format(args):
    template = str(args[0])
    parts = template.split("{}")
    result = parts[0]
    for i in range(1, len(parts)):
        if i <= len(args) - 1:
            result += str(args[i])
        result += parts[i]
    return result

def _str_find(args):
    s = str(args[0])
    sub = str(args[1])
    start = int(args[2]) if len(args) > 2 else 0
    idx = s.find(sub, start)
    return idx if idx >= 0 else None

def _str_count(args):
    return str(args[0]).count(str(args[1]))

def _str_title(args):
    return str(args[0]).title()

def _str_swapcase(args):
    return str(args[0]).swapcase()

LIB_STRING = {
    "repeat": BuiltinFunction("string.repeat", _str_repeat, min_args=2, max_args=2),
    "reverse": BuiltinFunction("string.reverse", _str_reverse, min_args=1, max_args=1),
    "pad_left": BuiltinFunction("string.pad_left", _str_pad_left, min_args=2, max_args=3),
    "pad_right": BuiltinFunction("string.pad_right", _str_pad_right, min_args=2, max_args=3),
    "format": BuiltinFunction("string.format", _str_format, min_args=1),
    "find": BuiltinFunction("string.find", _str_find, min_args=2, max_args=3),
    "count": BuiltinFunction("string.count", _str_count, min_args=2, max_args=2),
    "title": BuiltinFunction("string.title", _str_title, min_args=1, max_args=1),
    "swapcase": BuiltinFunction("string.swapcase", _str_swapcase, min_args=1, max_args=1),
}


# ---------------------------------------------------------------------------
# time
# ---------------------------------------------------------------------------

def _time_now(args):
    return _time.time()

def _time_ctime(args):
    ts = args[0] if args else None
    if ts is not None:
        return _time.ctime(float(ts))
    return _time.ctime()

def _time_sleep(args):
    _time.sleep(float(args[0]))
    return None

def _time_gmtime(args):
    ts = args[0] if args else None
    t = _time.gmtime(float(ts)) if ts is not None else _time.gmtime()
    return {
        "year": t.tm_year, "month": t.tm_mon, "day": t.tm_mday,
        "hour": t.tm_hour, "minute": t.tm_min, "second": t.tm_sec,
        "weekday": t.tm_wday, "yday": t.tm_yday,
    }

def _time_localtime(args):
    ts = args[0] if args else None
    t = _time.localtime(float(ts)) if ts is not None else _time.localtime()
    return {
        "year": t.tm_year, "month": t.tm_mon, "day": t.tm_mday,
        "hour": t.tm_hour, "minute": t.tm_min, "second": t.tm_sec,
        "weekday": t.tm_wday, "yday": t.tm_yday,
    }

def _time_strftime(args):
    fmt = str(args[0])
    ts = args[1] if len(args) > 1 else None
    t = _time.localtime(float(ts)) if ts is not None else _time.localtime()
    return _time.strftime(fmt, t)

def _time_strptime(args):
    s = str(args[0])
    fmt = str(args[1]) if len(args) > 1 else "%Y-%m-%d %H:%M:%S"
    t = _time.strptime(s, fmt)
    return _time.mktime(t)

LIB_TIME = {
    "now": BuiltinFunction("time.now", _time_now, min_args=0, max_args=0),
    "ctime": BuiltinFunction("time.ctime", _time_ctime, min_args=0, max_args=1),
    "sleep": BuiltinFunction("time.sleep", _time_sleep, min_args=1, max_args=1),
    "gmtime": BuiltinFunction("time.gmtime", _time_gmtime, min_args=0, max_args=1),
    "localtime": BuiltinFunction("time.localtime", _time_localtime, min_args=0, max_args=1),
    "strftime": BuiltinFunction("time.strftime", _time_strftime, min_args=1, max_args=2),
    "strptime": BuiltinFunction("time.strptime", _time_strptime, min_args=1, max_args=2),
}


# ---------------------------------------------------------------------------
# Register all libraries
# ---------------------------------------------------------------------------

LIBS = {
    "json": LIB_JSON,
    "math": LIB_MATH,
    "os": LIB_OS,
    "string": LIB_STRING,
    "time": LIB_TIME,
}
