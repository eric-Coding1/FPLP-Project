"""FPLP Language - Extension Libraries (json, math, os, string, time, sys, http, base64, hashlib, csv, re)"""

import json as _json
import math as _math
import os as _os
import sys as _sys
import time as _time
import datetime
import socket as _socket
import platform as _platform

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


# ===== OS 新增系统函数 =====

def _os_hostname(args):
    return _socket.gethostname()

def _os_username(args):
    return _os.environ.get("USERNAME") or _os.environ.get("USER") or "unknown"

def _os_pid(args):
    return _os.getpid()

def _os_cpu_count(args):
    return _os.cpu_count() or 1

def _os_platform(args):
    return _sys.platform

def _os_exec(args):
    """os.exec(cmd) — run shell command, return (exit_code, stdout_str)."""
    import subprocess as _sp
    try:
        r = _sp.run(str(args[0]), shell=True, capture_output=True, text=True, timeout=60)
        return {"code": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
    except _sp.TimeoutExpired:
        return {"code": -1, "stdout": "", "stderr": "timeout"}
    except Exception as e:
        return {"code": -2, "stdout": "", "stderr": str(e)}


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
    "hostname": BuiltinFunction("os.hostname", _os_hostname, min_args=0, max_args=0),
    "username": BuiltinFunction("os.username", _os_username, min_args=0, max_args=0),
    "pid": BuiltinFunction("os.pid", _os_pid, min_args=0, max_args=0),
    "cpu_count": BuiltinFunction("os.cpu_count", _os_cpu_count, min_args=0, max_args=0),
    "platform": BuiltinFunction("os.platform", _os_platform, min_args=0, max_args=0),
    "exec": BuiltinFunction("os.exec", _os_exec, min_args=1, max_args=1),
    "sep": _os.sep,
    "linesep": repr(_os.linesep),
}


# ======================================================================
# sys — 系统运行时信息
# ======================================================================

def _sys_argv(args):
    return _sys.argv[1:]  # skip script name

def _sys_exit(args):
    code = int(args[0]) if args else 0
    _sys.exit(code)

def _sys_version(args):
    return f"FPLP v1.0 (Python {_sys.version.split()[0]})"

def _sys_platform(args):
    return _sys.platform

def _sys_executable(args):
    return _sys.executable

def _sys_modules(args):
    return list(_sys.modules.keys())[:50]  # top 50 modules

def _sys_path(args):
    return _sys.path[:20]  # first 20 paths

def _sys_getsizeof(args):
    return _sys.getsizeof(args[0])

def _sys_gc(args):
    import gc
    if args and str(args[0]) == "collect":
        return gc.collect()
    return gc.get_count()

LIB_SYS = {
    "argv": BuiltinFunction("sys.argv", _sys_argv, min_args=0, max_args=0),
    "exit": BuiltinFunction("sys.exit", _sys_exit, min_args=0, max_args=1),
    "version": BuiltinFunction("sys.version", _sys_version, min_args=0, max_args=0),
    "platform": BuiltinFunction("sys.platform", _sys_platform, min_args=0, max_args=0),
    "executable": BuiltinFunction("sys.executable", _sys_executable, min_args=0, max_args=0),
    "modules": BuiltinFunction("sys.modules", _sys_modules, min_args=0, max_args=0),
    "path": BuiltinFunction("sys.path", _sys_path, min_args=0, max_args=0),
    "getsizeof": BuiltinFunction("sys.getsizeof", _sys_getsizeof, min_args=1, max_args=1),
    "gc": BuiltinFunction("sys.gc", _sys_gc, min_args=0, max_args=1),
}
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


# ======================================================================
# http — HTTP 客户端
# ======================================================================

def _http_get(args):
    import urllib.request as _ur
    url = str(args[0])
    try:
        with _ur.urlopen(url, timeout=10) as resp:
            return {
                "status": resp.status,
                "body": resp.read().decode("utf-8", errors="replace"),
                "headers": dict(resp.headers),
            }
    except Exception as e:
        return {"status": 0, "body": "", "headers": {}, "error": str(e)}

def _http_post(args):
    import urllib.request as _ur
    url = str(args[0])
    data = str(args[1]).encode("utf-8") if len(args) > 1 else b""
    content_type = str(args[2]) if len(args) > 2 else "application/x-www-form-urlencoded"
    try:
        req = _ur.Request(url, data=data, method="POST")
        req.add_header("Content-Type", content_type)
        with _ur.urlopen(req, timeout=10) as resp:
            return {
                "status": resp.status,
                "body": resp.read().decode("utf-8", errors="replace"),
                "headers": dict(resp.headers),
            }
    except Exception as e:
        return {"status": 0, "body": "", "headers": {}, "error": str(e)}

LIB_HTTP = {
    "get": BuiltinFunction("http.get", _http_get, min_args=1, max_args=1),
    "post": BuiltinFunction("http.post", _http_post, min_args=1, max_args=3),
}


# ======================================================================
# base64
# ======================================================================

import base64 as _base64

def _b64_encode(args):
    data = str(args[0]).encode("utf-8")
    return _base64.b64encode(data).decode("ascii")

def _b64_decode(args):
    return _base64.b64decode(str(args[0])).decode("utf-8", errors="replace")

LIB_BASE64 = {
    "encode": BuiltinFunction("base64.encode", _b64_encode, min_args=1, max_args=1),
    "decode": BuiltinFunction("base64.decode", _b64_decode, min_args=1, max_args=1),
}


# ======================================================================
# hashlib
# ======================================================================

import hashlib as _hashlib

def _hash_md5(args):
    return _hashlib.md5(str(args[0]).encode("utf-8")).hexdigest()

def _hash_sha1(args):
    return _hashlib.sha1(str(args[0]).encode("utf-8")).hexdigest()

def _hash_sha256(args):
    return _hashlib.sha256(str(args[0]).encode("utf-8")).hexdigest()

LIB_HASHLIB = {
    "md5": BuiltinFunction("hashlib.md5", _hash_md5, min_args=1, max_args=1),
    "sha1": BuiltinFunction("hashlib.sha1", _hash_sha1, min_args=1, max_args=1),
    "sha256": BuiltinFunction("hashlib.sha256", _hash_sha256, min_args=1, max_args=1),
}


# ======================================================================
# csv
# ======================================================================

import csv as _csv
import io as _io

def _csv_parse(args):
    text = str(args[0])
    has_header = args[1] if len(args) > 1 else False
    reader = _csv.reader(_io.StringIO(text))
    rows = list(reader)
    if has_header and rows:
        headers = rows[0]
        return [{headers[i]: row[i] for i in range(len(headers))} for row in rows[1:]]
    return rows

def _csv_stringify(args):
    data = args[0]
    if not isinstance(data, list):
        raise FPLPError("csv.stringify expects an array")
    buf = _io.StringIO()
    writer = _csv.writer(buf)
    for row in data:
        if isinstance(row, list):
            writer.writerow(row)
        elif isinstance(row, dict):
            writer.writerow(row.values())
    return buf.getvalue().strip()

LIB_CSV = {
    "parse": BuiltinFunction("csv.parse", _csv_parse, min_args=1, max_args=2),
    "stringify": BuiltinFunction("csv.stringify", _csv_stringify, min_args=1, max_args=1),
}


# ======================================================================
# re — 正则表达式
# ======================================================================

import re as _re

def _re_match(args):
    pattern = str(args[0])
    text = str(args[1])
    m = _re.match(pattern, text)
    if m:
        return {"start": m.start(), "end": m.end(), "groups": list(m.groups())}
    return None

def _re_search(args):
    pattern = str(args[0])
    text = str(args[1])
    m = _re.search(pattern, text)
    if m:
        return {"start": m.start(), "end": m.end(), "groups": list(m.groups())}
    return None

def _re_findall(args):
    pattern = str(args[0])
    text = str(args[1])
    return _re.findall(pattern, text)

def _re_split(args):
    pattern = str(args[0])
    text = str(args[1])
    return _re.split(pattern, text)

def _re_sub(args):
    pattern = str(args[0])
    repl = str(args[1])
    text = str(args[2])
    return _re.sub(pattern, repl, text)

def _re_escape(args):
    return _re.escape(str(args[0]))

LIB_RE = {
    "match": BuiltinFunction("re.match", _re_match, min_args=2, max_args=2),
    "search": BuiltinFunction("re.search", _re_search, min_args=2, max_args=2),
    "findall": BuiltinFunction("re.findall", _re_findall, min_args=2, max_args=2),
    "split": BuiltinFunction("re.split", _re_split, min_args=2, max_args=2),
    "sub": BuiltinFunction("re.sub", _re_sub, min_args=3, max_args=3),
    "escape": BuiltinFunction("re.escape", _re_escape, min_args=1, max_args=1),
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
    "sys": LIB_SYS,
    "http": LIB_HTTP,
    "base64": LIB_BASE64,
    "hashlib": LIB_HASHLIB,
    "csv": LIB_CSV,
    "re": LIB_RE,
}
