"""FPLP Language - Extension Libraries (json, math, os, string, time, sys, http, base64, hashlib, csv, re)"""

import json as _json
import math as _math
import os as _os
import sys as _sys
import time as _time
import datetime
import socket as _socket
import platform as _platform
import subprocess as _subprocess
import shutil as _shutil

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


# ======================================================================
# fuzzy — 模糊匹配与纠错
# ======================================================================

def _fuzzy_levenshtein(args):
    a = str(args[0])
    b = str(args[1])
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a):
        curr = [i + 1]
        for j, cb in enumerate(b):
            cost = 0 if ca == cb else 1
            curr.append(min(
                curr[j] + 1,       # deletion
                prev[j + 1] + 1,   # insertion
                prev[j] + cost     # substitution
            ))
        prev = curr
    return prev[-1]

def _fuzzy_closest(args):
    """fuzzy.closest(word, candidates) → returns best match or nil."""
    word = str(args[0])
    candidates = args[1]
    if not candidates:
        return None
    best = None
    best_dist = 4
    for c in candidates:
        d = _fuzzy_levenshtein([word, str(c)])
        if d < best_dist:
            best_dist = d
            best = c
    return best

LIB_FUZZY = {
    "distance": BuiltinFunction("fuzzy.distance", _fuzzy_levenshtein, min_args=2, max_args=2),
    "closest": BuiltinFunction("fuzzy.closest", _fuzzy_closest, min_args=2, max_args=2),
}

# ======================================================================
# path — 路径操作
# ======================================================================

def _path_join(args):
    return _os.path.join(*[str(a) for a in args])

def _path_basename(args):
    return _os.path.basename(str(args[0]))

def _path_dirname(args):
    return _os.path.dirname(str(args[0]))

def _path_splitext(args):
    root, ext = _os.path.splitext(str(args[0]))
    return {"root": root, "ext": ext}

def _path_abspath(args):
    return _os.path.abspath(str(args[0]))

def _path_expanduser(args):
    return _os.path.expanduser(str(args[0]))

def _path_relpath(args):
    path = str(args[0])
    start = str(args[1]) if len(args) > 1 else _os.getcwd()
    return _os.path.relpath(path, start)

def _path_split(args):
    parts = []
    p = str(args[0])
    while p:
        head, tail = _os.path.split(p)
        if not tail:
            if head:
                parts.insert(0, head)
            break
        parts.insert(0, tail)
        p = head
    return parts

def _path_size(args):
    return _os.path.getsize(str(args[0]))

def _path_mtime(args):
    return _os.path.getmtime(str(args[0]))

def _path_ismount(args):
    return _os.path.ismount(str(args[0]))

LIB_PATH = {
    "join": BuiltinFunction("path.join", _path_join, min_args=1),
    "basename": BuiltinFunction("path.basename", _path_basename, min_args=1, max_args=1),
    "dirname": BuiltinFunction("path.dirname", _path_dirname, min_args=1, max_args=1),
    "splitext": BuiltinFunction("path.splitext", _path_splitext, min_args=1, max_args=1),
    "abspath": BuiltinFunction("path.abspath", _path_abspath, min_args=1, max_args=1),
    "expanduser": BuiltinFunction("path.expanduser", _path_expanduser, min_args=1, max_args=1),
    "relpath": BuiltinFunction("path.relpath", _path_relpath, min_args=1, max_args=2),
    "split": BuiltinFunction("path.split", _path_split, min_args=1, max_args=1),
    "size": BuiltinFunction("path.size", _path_size, min_args=1, max_args=1),
    "mtime": BuiltinFunction("path.mtime", _path_mtime, min_args=1, max_args=1),
    "ismount": BuiltinFunction("path.ismount", _path_ismount, min_args=1, max_args=1),
}


# ======================================================================
# os 增强 — 文件系统 + 系统信息
# ======================================================================

def _os_copy(args):
    """Copy file src → dst."""
    src = str(args[0]); dst = str(args[1])
    _shutil.copy2(src, dst)
    return dst

def _os_copytree(args):
    """Copy directory recursively."""
    src = str(args[0]); dst = str(args[1])
    if _os.path.exists(dst):
        raise FPLPError(f"target exists: {dst}")
    _shutil.copytree(src, dst)
    return dst

def _os_move(args):
    """Move/rename file or directory."""
    src = str(args[0]); dst = str(args[1])
    _shutil.move(src, dst)
    return dst

def _os_glob(args):
    """Glob pattern matching."""
    import glob as _glob
    pattern = str(args[0])
    return _glob.glob(pattern, recursive=True)

def _os_walk(args):
    """Walk directory tree, return list of {dir, files, dirs}."""
    path = str(args[0])
    result = []
    for root, dirs, files in _os.walk(path):
        result.append({"dir": root, "dirs": dirs, "files": files})
    return result

def _os_which(args):
    """Find executable in PATH."""
    exe = _shutil.which(str(args[0]))
    return exe or None

def _os_tmpdir(args):
    import tempfile
    return tempfile.gettempdir()

def _os_tmpfile(args):
    import tempfile
    suffix = str(args[0]) if args else ".tmp"
    prefix = str(args[1]) if len(args) > 1 else "fplp_"
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    _os.close(fd)
    return path

def _os_disk_usage(args):
    """Disk usage stats for a path."""
    path = str(args[0]) if args else _os.getcwd()
    total, used, free = _shutil.disk_usage(path)
    return {"total": total, "used": used, "free": free}

def _os_symlink(args):
    src = str(args[0]); dst = str(args[1])
    _os.symlink(src, dst)
    return dst

def _os_chmod(args):
    path = str(args[0])
    mode = int(args[1]) if isinstance(args[1], (int, float)) else int(args[1])
    _os.chmod(path, mode)
    return True

def _os_stat(args):
    """File/directory stat info."""
    st = _os.stat(str(args[0]))
    return {
        "size": st.st_size,
        "mtime": st.st_mtime,
        "ctime": st.st_ctime,
        "atime": st.st_atime,
        "mode": st.st_mode,
        "uid": st.st_uid,
        "gid": st.st_gid,
        "is_dir": _os.path.isdir(str(args[0])),
        "is_file": _os.path.isfile(str(args[0])),
    }

def _os_env(args):
    """Get all environment variables as a dict."""
    return dict(_os.environ)

def _os_term_size(args):
    """Get terminal size as {columns, lines}."""
    try:
        size = _os.get_terminal_size()
        return {"columns": size.columns, "lines": size.lines}
    except Exception:
        return {"columns": 80, "lines": 24}

# Extend LIB_OS with new functions
LIB_OS.update({
    "copy": BuiltinFunction("os.copy", _os_copy, min_args=2, max_args=2),
    "copytree": BuiltinFunction("os.copytree", _os_copytree, min_args=2, max_args=2),
    "move": BuiltinFunction("os.move", _os_move, min_args=2, max_args=2),
    "glob": BuiltinFunction("os.glob", _os_glob, min_args=1, max_args=1),
    "walk": BuiltinFunction("os.walk", _os_walk, min_args=1, max_args=1),
    "which": BuiltinFunction("os.which", _os_which, min_args=1, max_args=1),
    "tmpdir": BuiltinFunction("os.tmpdir", _os_tmpdir, min_args=0, max_args=0),
    "tmpfile": BuiltinFunction("os.tmpfile", _os_tmpfile, min_args=0, max_args=2),
    "disk_usage": BuiltinFunction("os.disk_usage", _os_disk_usage, min_args=0, max_args=1),
    "symlink": BuiltinFunction("os.symlink", _os_symlink, min_args=2, max_args=2),
    "chmod": BuiltinFunction("os.chmod", _os_chmod, min_args=2, max_args=2),
    "stat": BuiltinFunction("os.stat", _os_stat, min_args=1, max_args=1),
    "env": BuiltinFunction("os.env", _os_env, min_args=0, max_args=0),
    "term_size": BuiltinFunction("os.term_size", _os_term_size, min_args=0, max_args=0),
})


# ======================================================================
# sys 增强 — 运行时 + 内省
# ======================================================================

def _sys_python_version(args):
    return _sys.version

def _sys_modules_list(args):
    return list(_sys.modules.keys())

def _sys_argv_raw(args):
    return _sys.argv

def _sys_exit_code(args):
    code = int(args[0]) if args else 0
    _sys.exit(code)

def _sys_refcount(args):
    import sys as _sys2
    return _sys2.getrefcount(args[0]) - 1  # subtract ref from getrefcount itself

# Extend LIB_SYS
LIB_SYS.update({
    "python_version": BuiltinFunction("sys.python_version", _sys_python_version, min_args=0, max_args=0),
    "modules_list": BuiltinFunction("sys.modules_list", _sys_modules_list, min_args=0, max_args=0),
    "argv_raw": BuiltinFunction("sys.argv_raw", _sys_argv_raw, min_args=0, max_args=0),
    "exit_code": BuiltinFunction("sys.exit_code", _sys_exit_code, min_args=0, max_args=1),
})


# ======================================================================
# proc — 进程管理
# ======================================================================


def _proc_spawn(args):
    """Spawn a process. Returns {pid, stdin, stdout, stderr}."""
    cmd = str(args[0])
    shell = bool(args[1]) if len(args) > 1 else False
    try:
        p = _subprocess.Popen(
            cmd if shell else cmd.split(),
            shell=shell,
            stdin=_subprocess.PIPE,
            stdout=_subprocess.PIPE,
            stderr=_subprocess.PIPE,
            text=True
        )
        return {"pid": p.pid, "process": p}
    except Exception as e:
        raise FPLPError(f"spawn failed: {e}")

def _proc_run(args):
    """Run a command and wait for completion. Returns {code, stdout, stderr}."""
    cmd = str(args[0])
    timeout_val = float(args[1]) if len(args) > 1 else 30
    try:
        r = _subprocess.run(
            cmd, shell=True, capture_output=True, text=True,
            timeout=timeout_val
        )
        return {"code": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
    except _subprocess.TimeoutExpired:
        return {"code": -1, "stdout": "", "stderr": "timeout"}
    except Exception as e:
        return {"code": -2, "stdout": "", "stderr": str(e)}

def _proc_kill(args):
    """Kill a process by PID."""
    pid = int(args[0])
    sig = int(args[1]) if len(args) > 1 else _signal.SIGTERM
    try:
        _os.kill(pid, sig)
        return True
    except ProcessLookupError:
        return False

def _proc_pid(args):
    """Current process ID."""
    return _os.getpid()

def _proc_ppid(args):
    """Parent process ID."""
    return _os.getppid()

def _proc_cwd(args):
    """Current working directory."""
    return _os.getcwd()

def _proc_chdir(args):
    """Change current working directory."""
    _os.chdir(str(args[0]))
    return True

def _proc_environ(args):
    """Get or set environment variables."""
    if not args:
        return dict(_os.environ)
    key = str(args[0])
    if len(args) > 1:
        _os.environ[key] = str(args[1])
        return True
    return _os.environ.get(key, None)

LIB_PROC = {
    "spawn": BuiltinFunction("proc.spawn", _proc_spawn, min_args=1, max_args=2),
    "run": BuiltinFunction("proc.run", _proc_run, min_args=1, max_args=2),
    "kill": BuiltinFunction("proc.kill", _proc_kill, min_args=1, max_args=2),
    "pid": BuiltinFunction("proc.pid", _proc_pid, min_args=0, max_args=0),
    "ppid": BuiltinFunction("proc.ppid", _proc_ppid, min_args=0, max_args=0),
    "cwd": BuiltinFunction("proc.cwd", _proc_cwd, min_args=0, max_args=0),
    "chdir": BuiltinFunction("proc.chdir", _proc_chdir, min_args=1, max_args=1),
    "environ": BuiltinFunction("proc.environ", _proc_environ, min_args=0, max_args=2),
}


# ======================================================================
# net — 网络工具
# ======================================================================

def _net_hostname(args):
    return _socket.gethostname()

def _net_ip(args):
    """Get local IP address."""
    hostname = _socket.gethostname()
    try:
        return _socket.gethostbyname(hostname)
    except Exception:
        # Fallback method
        s = _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        try:
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            return ip
        except Exception:
            return "127.0.0.1"
        finally:
            s.close()

def _net_lookup(args):
    """DNS lookup: hostname → IP."""
    try:
        return _socket.gethostbyname(str(args[0]))
    except _socket.gaierror:
        return None

def _net_ping(args):
    """Ping a host (via system ping command). Returns {code, time_ms}."""
    host = str(args[0])
    count = int(args[1]) if len(args) > 1 else 1
    try:
        r = _subprocess.run(
            ["ping", "-n", str(count), host] if _sys.platform == "win32"
            else ["ping", "-c", str(count), host],
            capture_output=True, text=True, timeout=10
        )
        # Try to parse time from output
        import re as _re2
        times = _re2.findall(r"time[=<](\d+\.?\d*)", r.stdout.lower())
        return {
            "code": r.returncode,
            "time_ms": float(times[0]) if times else None,
            "output": r.stdout
        }
    except Exception as e:
        return {"code": -1, "time_ms": None, "output": str(e)}

LIB_NET = {
    "hostname": BuiltinFunction("net.hostname", _net_hostname, min_args=0, max_args=0),
    "ip": BuiltinFunction("net.ip", _net_ip, min_args=0, max_args=0),
    "lookup": BuiltinFunction("net.lookup", _net_lookup, min_args=1, max_args=1),
    "ping": BuiltinFunction("net.ping", _net_ping, min_args=1, max_args=2),
}


# ======================================================================
# io — 流式文件操作
# ======================================================================

def _io_read_lines(args):
    """Read file as list of lines."""
    path = str(args[0])
    with open(path, "r", encoding="utf-8") as f:
        return [line.rstrip("\n\r") for line in f]

def _io_write_lines(args):
    """Write list of lines to file."""
    path = str(args[0])
    lines = args[1]
    with open(path, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line) + "\n")
    return True

def _io_append_lines(args):
    """Append list of lines to file."""
    path = str(args[0])
    lines = args[1]
    with open(path, "a", encoding="utf-8") as f:
        for line in lines:
            f.write(str(line) + "\n")
    return True

def _io_read_bytes(args):
    """Read file as bytes, return list of integers."""
    path = str(args[0])
    with open(path, "rb") as f:
        data = f.read()
    return list(data)

def _io_write_bytes(args):
    """Write list of integers as bytes to file."""
    path = str(args[0])
    data = bytes(int(b) for b in args[1])
    with open(path, "wb") as f:
        f.write(data)
    return True

def _io_pipe(args):
    """Pipe data through a shell command. Returns stdout string."""
    cmd = str(args[0])
    input_data = str(args[1]) if len(args) > 1 else ""
    try:
        r = _subprocess.run(
            cmd, shell=True, input=input_data,
            capture_output=True, text=True, timeout=30
        )
        return {"code": r.returncode, "stdout": r.stdout, "stderr": r.stderr}
    except _subprocess.TimeoutExpired:
        return {"code": -1, "stdout": "", "stderr": "timeout"}

LIB_IO = {
    "read_lines": BuiltinFunction("io.read_lines", _io_read_lines, min_args=1, max_args=1),
    "write_lines": BuiltinFunction("io.write_lines", _io_write_lines, min_args=2, max_args=2),
    "append_lines": BuiltinFunction("io.append_lines", _io_append_lines, min_args=2, max_args=2),
    "read_bytes": BuiltinFunction("io.read_bytes", _io_read_bytes, min_args=1, max_args=1),
    "write_bytes": BuiltinFunction("io.write_bytes", _io_write_bytes, min_args=2, max_args=2),
    "pipe": BuiltinFunction("io.pipe", _io_pipe, min_args=1, max_args=2),
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
    "path": LIB_PATH,
    "proc": LIB_PROC,
    "net": LIB_NET,
    "io": LIB_IO,
    "fuzzy": LIB_FUZZY,
}
