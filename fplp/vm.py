"""FPLP Language - Stack-based Bytecode VM (Turbo v2)"""

from .bytecode import *
from .builtins import BUILTINS, FPLPError
from .environment import Environment


class VMError(Exception):
    pass


class Closure:
    __slots__ = ('code', 'env', 'arity')
    def __init__(self, code, env):
        self.code = code; self.env = env; self.arity = code.arity
    def __str__(self): return f"<fn {self.code.name}>"
    __repr__ = __str__


class Frame:
    __slots__ = ('code', 'ip', 'env')
    def __init__(self, code, env):
        self.code = code; self.ip = 0; self.env = env


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

def _build():
    t = [None] * 128

    # Handlers receive (vm, frame, arg, code)
    # They manipulate vm.sp and vm.stack DIRECTLY (no helper calls)

    t[PUSH_NIL]   = lambda vm, f, a, c: _s(vm, None)
    t[PUSH_TRUE]  = lambda vm, f, a, c: _s(vm, True)
    t[PUSH_FALSE] = lambda vm, f, a, c: _s(vm, False)
    t[PUSH_INT]   = lambda vm, f, a, c: _s(vm, c.consts[a])
    t[PUSH_FLOAT] = lambda vm, f, a, c: _s(vm, c.consts[a])
    t[PUSH_STR]   = lambda vm, f, a, c: _s(vm, c.consts[a])
    t[POP]        = lambda vm, f, a, c: _x(vm)
    t[DUP]        = lambda vm, f, a, c: _d(vm)
    t[NOP]        = lambda vm, f, a, c: None

    def _LOAD(vm, f, a, c):
        name = c.names[a]
        env = f.env
        while env:
            if name in env.store:
                _s(vm, env.store[name]); return
            env = env.outer
        if name in BUILTINS:
            _s(vm, BUILTINS[name]); return
        hint = _suggest_name(name, f.env)
        msg = f"undefined variable '{name}'"
        if hint: msg += f" (did you mean '{hint}'?)"
        raise VMError(msg)

    def _STORE(vm, f, a, c):
        val = vm.stack[vm.sp]; vm.sp -= 1
        name = c.names[a]
        env = f.env
        while env:
            if name in env.store:
                env.store[name] = val
                _s(vm, val); return
            env = env.outer
        hint = _suggest_name(name, f.env)
        msg = f"undefined variable '{name}'"
        if hint: msg += f" (did you mean '{hint}'?)"
        raise VMError(msg)

    def _DEFINE(vm, f, a, c):
        val = vm.stack[vm.sp]; vm.sp -= 1
        f.env.store[c.names[a]] = val

    t[LOAD] = _LOAD; t[STORE] = _STORE; t[DEFINE] = _DEFINE

    def _ADD(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1
        if isinstance(l, str):
            _s(vm, l + r if isinstance(r, str) else l + str(r))
        else:
            _s(vm, l + r)

    def _SUB(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1; _s(vm, l - r)
    def _MUL(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1
        _s(vm, l * r if not isinstance(l, str) else l * r)
    def _DIV(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1
        if r == 0: raise VMError("div by zero")
        d = l / r
        if isinstance(d, float) and d == int(d) and not isinstance(l, float) and not isinstance(r, float): d = int(d)
        _s(vm, d)
    def _MOD(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1
        if r == 0: raise VMError("mod by zero")
        _s(vm, l % r)

    t[ADD] = _ADD; t[SUB] = _SUB; t[MUL] = _MUL; t[DIV] = _DIV; t[MOD] = _MOD
    t[NEG] = lambda vm, f, a, c: vm.stack.__setitem__(vm.sp, -vm.stack[vm.sp])
    t[POS] = lambda vm, f, a, c: None
    t[INC] = lambda vm, f, a, c: vm.stack.__setitem__(vm.sp, vm.stack[vm.sp] + 1)

    # Comparisons
    def _CMP(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1
        op = a  # encode comparison type in arg
        if op == 0: _s(vm, l == r)
        elif op == 1: _s(vm, l != r)
        elif op == 2: _s(vm, l < r)
        elif op == 3: _s(vm, l > r)
        elif op == 4: _s(vm, l <= r)
        elif op == 5: _s(vm, l >= r)

    # Encode comparison type in the arg
    # We need to patch these at build time
    # Instead, use separate handlers
    def _EQ(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1; _s(vm, _deep_eq(l, r))
    def _NE(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1; _s(vm, not _deep_eq(l, r))
    def _LT(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1; _s(vm, l < r)
    def _GT(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1; _s(vm, l > r)
    def _LE(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1; _s(vm, l <= r)
    def _GE(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        l = vm.stack[vm.sp]; vm.sp -= 1; _s(vm, l >= r)

    t[EQ] = _EQ; t[NE] = _NE; t[LT] = _LT; t[GT] = _GT; t[LE] = _LE; t[GE] = _GE
    t[NOT] = lambda vm, f, a, c: vm.stack.__setitem__(vm.sp, not _truthy(vm.stack[vm.sp]))

    # Control
    t[JMP] = lambda vm, f, a, c: setattr(f, 'ip', a)
    t[JIF] = lambda vm, f, a, c: _jif(vm, f, a)

    # Functions
    def _MKFN(vm, f, a, c): _s(vm, Closure(c.fn_objects[a], f.env))

    def _CALL(vm, f, a, c):
        fn_val = vm.stack[vm.sp]; vm.sp -= 1
        n = a
        if n:
            args = [vm.stack[vm.sp - n + 1 + i] for i in range(n)]
            vm.sp -= n
        else:
            args = []

        if isinstance(fn_val, Closure):
            cl = fn_val
            if len(args) != cl.arity:
                raise VMError(f"expected {cl.arity} args, got {len(args)}")
            env = Environment(cl.env)
            for i in range(cl.arity):
                env.store[cl.code.names[i]] = args[i]
            vm.frames.append(Frame(cl.code, env))
        elif hasattr(fn_val, 'call'):
            _s(vm, fn_val.call(args))
        else:
            raise VMError(f"'{fn_val}' not callable")

    def _RET(vm, f, a, c):
        r = vm.stack[vm.sp]; vm.sp -= 1
        vm.frames.pop()
        if vm.frames: _s(vm, r)

    t[MKFN] = _MKFN; t[CALL] = _CALL; t[RET] = _RET

    # Data
    t[MKARR] = lambda vm, f, a, c: _mkarr(vm, a)
    t[MKOBJ] = lambda vm, f, a, c: _mkobj(vm, a)

    def _INDEX(vm, f, a, c):
        idx = vm.stack[vm.sp]; vm.sp -= 1
        obj = vm.stack[vm.sp]; vm.sp -= 1
        if isinstance(obj, (list, str)):
            if not isinstance(idx, int): raise VMError("index must be int")
            if idx < 0 or idx >= len(obj): raise VMError("index out of range")
            _s(vm, obj[idx])
        elif isinstance(obj, dict): _s(vm, obj.get(idx, None))
        else: raise VMError(f"cannot index {type(obj).__name__}")
    t[INDEX] = _INDEX

    t[BUILTIN] = lambda vm, f, a, c: _s(vm, BUILTINS[c.builtins[a]])
    t[HALT] = lambda vm, f, a, c: vm.frames.clear()
    t[LEN] = lambda vm, f, a, c: _len_op(vm)

    return t


# Hoisted helpers
def _s(vm, v):  # push
    vm.sp += 1; vm.stack[vm.sp] = v

def _x(vm):  # pop
    vm.sp -= 1

def _d(vm):  # dup
    v = vm.stack[vm.sp]; vm.sp += 1; vm.stack[vm.sp] = v

def _truthy(val):
    if val is None or val is False: return False
    if val is True: return True
    if isinstance(val, (int, float)): return val != 0
    if isinstance(val, (str, list, dict)): return len(val) > 0
    return True

def _deep_eq(a, b):
    if type(a) != type(b): return False
    if isinstance(a, dict):
        if len(a) != len(b): return False
        for k in a:
            if k not in b or not _deep_eq(a[k], b[k]): return False
        return True
    if isinstance(a, list):
        if len(a) != len(b): return False
        return all(_deep_eq(x, y) for x, y in zip(a, b))
    return a == b

def _mkarr(vm, n):
    sp = vm.sp
    vm.sp -= (n - 1)
    vm.stack[vm.sp] = [vm.stack[sp - n + 1 + i] for i in range(n)]

def _mkobj(vm, n):
    sp = vm.sp
    base = sp - n * 2 + 1
    d = {}
    for i in range(n):
        d[vm.stack[base + i*2]] = vm.stack[base + i*2 + 1]
    vm.sp -= (n * 2 - 1)
    vm.stack[vm.sp] = d

def _len_op(vm):
    val = vm.stack[vm.sp]
    if isinstance(val, (str, list, dict)):
        vm.stack[vm.sp] = len(val)
    else:
        raise VMError(f"len() not supported for {type(val).__name__}")


def _jif(vm, f, a):
    if not _truthy(vm.stack[vm.sp]):
        f.ip = a
    vm.sp -= 1


# ---------------------------------------------------------------------------
# Variable name suggestion for auto-correction
# ---------------------------------------------------------------------------

def _suggest_name(name, env):
    """Find the closest known variable name to a mistyped one."""
    from .fuzzy import suggest_variable

    # Collect all visible variable names
    known = set()
    e = env
    while e:
        known.update(e.store.keys())
        e = e.outer

    if not known:
        return None

    suggested, dist = suggest_variable(name, known, max_distance=3)
    return suggested


_DISPATCH = _build()


# ---------------------------------------------------------------------------
# VM
# ---------------------------------------------------------------------------

class VM:
    def __init__(self, stack_size=8192):
        self.stack = [None] * stack_size
        self.STACK_SIZE = stack_size
        self.sp = -1
        self.frames = []

    def reset(self):
        """Reuse this VM by clearing frames and stack."""
        self.frames.clear()
        # Only clear used portion of stack
        for i in range(self.sp + 1):
            self.stack[i] = None
        self.sp = -1

    def run_code(self, code, env=None):
        self.reset()
        if env is None:
            env = Environment()
        self.frames.append(Frame(code, env))
        return self._exec()

    def _exec(self):
        frames = self.frames
        dispatch = _DISPATCH
        while frames:
            frame = frames[-1]
            ip = frame.ip
            instrs = frame.code.instrs
            if ip >= len(instrs):
                break
            ins = instrs[ip]
            frame.ip = ip + 1
            h = dispatch[ins.op]
            try:
                h(self, frame, ins.arg, frame.code)
            except VMError:
                raise
            except FPLPError:
                raise
            except Exception as e:
                raise VMError(f"VM error IP {frame.ip-1} in {frame.code.name}: {e}")

        sp = self.sp
        if sp >= 0:
            r = self.stack[sp]
            self.stack[sp] = None
            self.sp = sp - 1
            return r
        return None
