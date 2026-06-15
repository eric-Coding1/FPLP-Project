"""FPLP Language - Package Manager (like pip for FPLP)

Usage:
    from fplp.pkg import install, installed_packages, search_packages
    
CLI:
    python main.py --install <name>
    python main.py --pkg-list
    python main.py --pkg-search <query>
"""

import os
import sys
import json
import urllib.request
import urllib.error

# Package directory
PKG_DIR = os.path.expanduser("~/.fplp/packages")
REGISTRY_URL = "https://gitee.com/eric_Coding/fplp-packages/raw/main/registry.json"

# In-memory loaded packages
_loaded = {}


def _ensure_dir():
    os.makedirs(PKG_DIR, exist_ok=True)


def _fetch_registry():
    """Fetch the package registry from Gitee."""
    try:
        req = urllib.request.urlopen(REGISTRY_URL, timeout=10)
        data = req.read().decode("utf-8")
        return json.loads(data)
    except Exception as e:
        print(f"[pkg] Warning: cannot fetch registry: {e}")
        return {}


def search_packages(query=""):
    """Search available packages in the registry."""
    registry = _fetch_registry()
    if not registry:
        print("[pkg] No registry available (offline or no internet)")
        return []

    results = []
    q = query.lower()
    for name, info in registry.items():
        if q in name.lower() or q in info.get("description", "").lower():
            results.append((name, info))
    return results


def list_available():
    """List all available packages from registry."""
    registry = _fetch_registry()
    return list(registry.items()) if registry else []


def installed_packages():
    """List installed packages."""
    _ensure_dir()
    installed = []
    for fname in os.listdir(PKG_DIR):
        if fname.endswith(".fplp"):
            name = fname[:-5]
            path = os.path.join(PKG_DIR, fname)
            mtime = os.path.getmtime(path)
            size = os.path.getsize(path)
            installed.append((name, path, mtime, size))
    return installed


def install(name):
    """Download and install a package from the registry."""
    _ensure_dir()
    registry = _fetch_registry()

    if name not in registry:
        print(f"[pkg] Package '{name}' not found in registry.")
        similar = [k for k in registry if name[:3] in k]
        if similar:
            print(f"    Did you mean: {', '.join(similar[:5])}?")
        return False

    info = registry[name]
    url = info.get("url")
    if not url:
        print(f"[pkg] Package '{name}' has no download URL.")
        return False

    dest = os.path.join(PKG_DIR, f"{name}.fplp")
    print(f"[pkg] Downloading {name} v{info.get('version', '?')}...")
    print(f"    from: {url}")

    try:
        req = urllib.request.urlopen(url, timeout=30)
        content = req.read().decode("utf-8")

        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)

        print(f"[pkg] Installed: {name} ({len(content)} bytes)")
        print(f"    {info.get('description', '')}")
        return True

    except urllib.error.HTTPError as e:
        print(f"[pkg] Download failed: HTTP {e.code} {e.reason}")
        return False
    except Exception as e:
        print(f"[pkg] Error: {e}")
        return False


def remove(name):
    """Uninstall a package."""
    _ensure_dir()
    path = os.path.join(PKG_DIR, f"{name}.fplp")
    if os.path.exists(path):
        os.remove(path)
        print(f"[pkg] Removed: {name}")
        if name in _loaded:
            del _loaded[name]
        return True
    print(f"[pkg] Package '{name}' not installed.")
    return False


def load_installed(env=None):
    """Load all installed packages into an environment."""
    _ensure_dir()
    if env is None:
        env = {}

    # Populate builtin wrappers for packages that use them
    from fplp.builtins import BUILTINS
    for name, fn in BUILTINS.items():
        if hasattr(fn, "call"):
            def make_wrapper(f=fn):
                return lambda *args, **kw: f.call(list(args))
            env[name] = make_wrapper()

    count = 0
    # Also add math, os, json etc. from Python for package use
    import math, json, os as os_mod, re, random, time, hashlib, base64
    env.update({
        "PY_math": math, "PY_json": json, "PY_os": os_mod,
        "PY_re": re, "PY_random": random, "PY_time": time,
        "PY_hashlib": hashlib, "PY_base64": base64,
    })

    for fname in sorted(os.listdir(PKG_DIR)):
        if fname.endswith(".fplp") and fname not in _loaded:
            name = fname[:-5]
            path = os.path.join(PKG_DIR, fname)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    source = f.read()
                # Compile and execute
                compiled = compile(source, path, "exec")
                exec(compiled, env)
                _loaded[name] = True
                count += 1
            except Exception as e:
                print(f"[pkg] Error loading '{name}': {e}")

    if count:
        print(f"[pkg] Loaded {count} package(s)")
    return env


def make_sample_package(name):
    """Create a sample package file for testing."""
    _ensure_dir()
    samples = {
        "fplp-hello": """
# fplp-hello: Example package
print("[fplp-hello] Loaded! Try: hello()")

fn hello() {
    print("Hello from FPLP package manager!")
}

fn greet(name) {
    print("Hello,", name + "!")
}
""",
        "fplp-stats": """
# fplp-stats: Basic statistics
print("[fplp-stats] Loaded! Try: mean(), median()")

fn mean(arr) {
    let s = 0
    for x in arr { s = s + x }
    return s / len(arr)
}

fn median(arr) {
    sort(arr)
    let n = len(arr)
    if n % 2 == 0 {
        return (arr[n/2 - 1] + arr[n/2]) / 2
    }
    return arr[n/2]
}

fn stddev(arr) {
    let m = mean(arr)
    let sq = 0
    for x in arr { sq = sq + (x - m) * (x - m) }
    return sqrt(sq / len(arr))
}
""",
        "fplp-colors": """
# fplp-colors: Color manipulation
print("[fplp-colors] Loaded! Try: rgb(), hex_to_rgb()")

fn rgb(r, g, b) {
    return create_image(100, 100, r * 65536 + g * 256 + b)
}

fn hex_to_rgb(hex) {
    return {"r": 0, "g": 0, "b": 0}
}
""",
    }

    if name in samples:
        path = os.path.join(PKG_DIR, f"{name}.fplp")
        with open(path, "w", encoding="utf-8") as f:
            f.write(samples[name])
        print(f"[pkg] Created sample: {name}")
        return True
    return False
