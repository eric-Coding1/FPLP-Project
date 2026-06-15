# FPLP — Fast Parallel Language Plus

> A lightweight scripting language with bytecode compiler, stack VM, graphics editing, and Scratch-style block editor.

FPLP is a lightweight scripting language implemented in Python. It features dynamic typing, first-class functions, closures, and recursion. The language uses a **Pratt recursive descent parser**, a **bytecode compiler** that generates 29 opcodes, and a **stack-based virtual machine** for execution. It ships with 40+ built-in functions, Pillow-based image editing, and a desktop GUI with a Scratch-style block editor.

---

## ✨ Features

- **Minimal syntax** — Only 10 keywords, familiar Python/JavaScript-like syntax
- **Dynamic typing** — int, float, string, bool, nil, array, map
- **First-class functions** — Anonymous functions, closures, recursion, HOFs
- **Arrow syntax** — `fn name(p) => expr` with implicit return
- **Bytecode compiler** — AST → 29 instructions → stack VM
- **1.8x speedup** — vs. tree-walking interpreter
- **40+ built-in functions** — String, math, file I/O, collection operations
- **Image editing** — 18 Pillow functions: `draw_rect`, `blur`, `rotate`, etc.
- **5 extension libraries** — `json`, `math`, `os`, `string`, `time`
- **Scratch blocks** — 10 categories, 54 blocks, drag-and-drop programming
- **Desktop GUI** — tkinter editor + console + image preview

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Pillow (for image editing): `pip install Pillow`

### Launch

```bash
# GUI mode (default)
python main.py

# CLI REPL
python main.py --cli

# Run a file directly
python main.py examples/demo.fplp
```

### Hello World

```lpp
fn greet(name) => "Hello, " + name
print(greet("FPLP"))
print("2 + 3 * 4 =", 2 + 3 * 4)

let nums = [1, 2, 3, 4, 5]
let total = 0
for n in nums {
    total = total + n
}
print("sum =", total)
```

---

## 📖 Language Reference

### Variables

```lpp
let x = 42            # declaration
let name = "FPLP"
let pi = 3.14
x = 100               # re-assignment
```

### Control Flow

```lpp
# if / else
if score >= 90 {
    print("A")
} else if score >= 80 {
    print("B")
} else {
    print("C")
}

# for-each loop
for i in range(5) { print(i) }
for f in ["apple", "banana"] { print(f) }

# while loop
loop n > 0 { n = n - 1 }
```

### Functions

```lpp
# Block syntax
fn add(x, y) {
    return x + y
}

# Arrow syntax (implicit return)
fn add(x, y) => x + y

# Anonymous function
let mul = fn(a, b) => a * b

# Recursion
fn fib(n) {
    if n <= 1 { return n }
    return fib(n - 1) + fib(n - 2)
}

# Closure
fn make_adder(x) => fn(y) => x + y
let add5 = make_adder(5)
print(add5(3))    # 8
```

### Graphics (Image Editing)

```lpp
let img = create_image(400, 300, "#1a1a2e")
draw_rect(img, 50, 40, 120, 80, "#e94560")
draw_circle(img, 200, 150, 50, "#f5a623")
draw_text(img, 60, 200, "Hello FPLP!", 32, "white")
save_image(img, "output.png")
show_image(img)
```

### Extension Libraries

```lpp
json.stringify(data, 2)      # Pretty-printed JSON
math.sqrt(144)               # Math library
os.listdir(".")              # File system
string.repeat("ha", 3)       # String utilities
time.strftime("%Y-%m-%d")    # Time formatting
```

---

## 🏗 Project Structure

```
main.py              # Entry point (REPL + file runner + GUI)
fplp/
  lexer.py           # Lexer / tokenizer
  parser.py          # Pratt recursive descent parser
  ast_nodes.py       # AST node definitions
  compiler.py        # AST → bytecode compiler + peephole optimizer
  vm.py              # Stack-based virtual machine
  bytecode.py        # Instruction set definition
  environment.py     # Variable scope management
  evaluator.py       # Tree-walking interpreter (fallback)
  builtins.py        # 40+ built-in functions
  graphics.py        # Image editing (Pillow)
  libs.py            # Extension libraries (json/math/os/string/time)
  block_editor.py    # Scratch-style block editor
  gui.py             # tkinter desktop GUI
examples/            # Example scripts
fplp_icon.png        # Language icon
fplp.bat             # Windows launcher
```

---

## ⚡ Performance

Benchmark: running `demo.fplp` 100 times, comparing with the tree-walking interpreter.

| Engine | Time | Speedup |
|--------|------|---------|
| Tree-walking interpreter | 2.6ms | 1.0x |
| Stack VM | 1.5ms | **1.8x** |

Optimizations: dispatch table instruction dispatch, inlined push/pop, inlined environment traversal, VM reuse.

---

## 📄 License

MIT License
