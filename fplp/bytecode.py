"""FPLP Language - Bytecode Instruction Set & Code Objects"""

# === Opcodes ===

# Stack
NOP = 0
POP = 1
DUP = 2        # duplicate top of stack

# Constants
PUSH_NIL = 10
PUSH_TRUE = 11
PUSH_FALSE = 12
PUSH_INT = 13      # arg = int value
PUSH_FLOAT = 14    # arg = float value
PUSH_STR = 15      # arg = string value

# Variables (arg = name index in names list)
LOAD = 20      # push variable value
STORE = 21     # pop and assign to existing variable
DEFINE = 22    # pop and create new variable

# Arithmetic
ADD = 30
SUB = 31
MUL = 32
DIV = 33
MOD = 34
NEG = 35       # unary minus
POS = 36       # unary plus
INC = 37       # increment top of stack by 1 (for loop iteration)
LEN = 38       # len of top of stack

# Comparison
EQ = 40
NE = 41
LT = 42
GT = 43
LE = 44
GE = 45

# Logical
NOT = 50

# Control flow
JMP = 60       # unconditional jump (arg = target index)
JIF = 61       # jump if false/truthy, pop condition (arg = target index)

# Functions
CALL = 70      # arg = num args
RET = 71       # return from function
MKFN = 72      # make function (arg = code object index)
CLOSURE = 73   # make closure with captured vars

# Data structures
MKARR = 80     # make array (arg = num elements, pop that many)
MKOBJ = 81     # make map (arg = num pairs, pop 2*num items: k1,v1,k2,v2...)
INDEX = 82     # index access: pop index, pop obj, push result

# Misc
BUILTIN = 90   # push builtin function by name index
HALT = 99


OP_NAMES = {
    NOP: "NOP", POP: "POP", DUP: "DUP",
    PUSH_NIL: "PUSH_NIL", PUSH_TRUE: "PUSH_TRUE", PUSH_FALSE: "PUSH_FALSE",
    PUSH_INT: "PUSH_INT", PUSH_FLOAT: "PUSH_FLOAT", PUSH_STR: "PUSH_STR",
    LOAD: "LOAD", STORE: "STORE", DEFINE: "DEFINE",
    ADD: "ADD", SUB: "SUB", MUL: "MUL", DIV: "DIV", MOD: "MOD",
    NEG: "NEG", POS: "POS", INC: "INC", LEN: "LEN",
    EQ: "EQ", NE: "NE", LT: "LT", GT: "GT", LE: "LE", GE: "GE",
    NOT: "NOT",
    JMP: "JMP", JIF: "JIF",
    CALL: "CALL", RET: "RET", MKFN: "MKFN", CLOSURE: "CLOSURE",
    MKARR: "MKARR", MKOBJ: "MKOBJ", INDEX: "INDEX",
    BUILTIN: "BUILTIN", HALT: "HALT",
}


class Instruction:
    """A single bytecode instruction."""
    __slots__ = ('op', 'arg')

    def __init__(self, op, arg=None):
        self.op = op
        self.arg = arg

    def __repr__(self):
        name = OP_NAMES.get(self.op, f"OP_{self.op}")
        if self.arg is not None:
            return f"  {name:<12} {self.arg}"
        return f"  {name}"

    def __eq__(self, other):
        if isinstance(other, Instruction):
            return self.op == other.op and self.arg == other.arg
        return NotImplemented


class CodeObject:
    """
    Compiled code.
    - instrs: list of Instruction
    - consts: list of literal values (int, float, str, None, bool)
    - names: list of variable name strings
    - builtins: list of builtin function name strings
    - fn_objects: list of nested CodeObjects (for closures)
    - arity: number of parameters (for functions)
    - name: human-readable name
    """

    def __init__(self, name="<anon>", arity=0):
        self.instrs = []
        self.consts = []
        self.names = []
        self.builtins = []
        self.fn_objects = []
        self.arity = arity
        self.name = name

    def add_instr(self, op, arg=None):
        self.instrs.append(Instruction(op, arg))
        return len(self.instrs) - 1  # return index for patching

    def patch_jump(self, idx, target):
        """Patch a jump instruction's argument."""
        self.instrs[idx].arg = target

    def add_const(self, value):
        """Add constant and return its index."""
        # Reuse existing constants (for small ints and common strings)
        for i, c in enumerate(self.consts):
            if type(c) is type(value) and c == value:
                return i
        self.consts.append(value)
        return len(self.consts) - 1

    def add_name(self, name):
        """Add name string and return its index."""
        for i, n in enumerate(self.names):
            if n == name:
                return i
        self.names.append(name)
        return len(self.names) - 1

    def add_builtin(self, name):
        """Add builtin name and return its index."""
        for i, n in enumerate(self.builtins):
            if n == name:
                return i
        self.builtins.append(name)
        return len(self.builtins) - 1

    def add_fn_obj(self, code_obj):
        """Add nested code object and return its index."""
        self.fn_objects.append(code_obj)
        return len(self.fn_objects) - 1

    def __repr__(self):
        lines = [f"--- {self.name} (arity={self.arity}) ---"]
        for i, ins in enumerate(self.instrs):
            lines.append(f"{i:4d} {ins}")
        lines.append(f"  consts: {self.consts}")
        lines.append(f"  names: {self.names}")
        lines.append(f"  builtins: {self.builtins}")
        return '\n'.join(lines)
