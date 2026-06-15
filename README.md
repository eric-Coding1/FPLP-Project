# FPLP — Fast Parallel Language Plus

> 自研轻量级脚本语言 · 字节码编译 + 栈式虚拟机 · 图形编辑 · GUI 积木模式

FPLP 是一款使用 Python 实现的轻量级脚本语言，支持动态类型、一等函数、闭包、递归等现代语言特性。它采用 **Pratt 递归下降解析器** 解析源码，通过 **字节码编译器** 生成指令，最终由 **栈式虚拟机** 执行。内置 40+ 实用函数，基于 Pillow 提供图形编辑能力，并附带 Scratch 风格积木编辑器的桌面 GUI。

---

## ✨ 特性

- **极致简洁** — 仅 10 个关键字，语法类似 Python/JavaScript
- **动态类型** — int, float, string, bool, nil, array, map
- **一等函数** — 匿名函数、闭包、递归、高阶函数
- **箭头语法** — `fn name(p) => expr` 自动 return
- **字节码编译器** — AST → 29 条指令集 → 栈式 VM
- **1.8x 加速** — 对比树遍历解释器
- **40+ 内置函数** — 字符串、数学、文件 IO、集合操作
- **图形编辑** — 18 个 Pillow 函数：`draw_rect`, `blur`, `rotate` 等
- **5 个扩展库** — `json`, `math`, `os`, `string`, `time`
- **Scratch 积木** — 10 个类别、54 个积木块的拖拽编程
- **桌面 GUI** — tkinter 编辑器 + 控制台 + 图片预览

---

## 🚀 快速开始

### 依赖

- Python 3.10+
- Pillow（图像编辑）：`pip install Pillow`

### 启动

```bash
# 图形界面（默认）
python main.py

# 命令行 REPL
python main.py --cli

# 直接运行文件
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

## 📖 语法速览

### 变量

```lpp
let x = 42            # 声明
let name = "FPLP"
let pi = 3.14
x = 100               # 重新赋值
```

### 控制流

```lpp
# if / else
if score >= 90 {
    print("A")
} else if score >= 80 {
    print("B")
} else {
    print("C")
}

# for-each 循环
for i in range(5) { print(i) }
for f in ["苹果", "香蕉"] { print(f) }

# while 循环
loop n > 0 { n = n - 1 }
```

### 函数

```lpp
# 传统语法
fn add(x, y) {
    return x + y
}

# 箭头简写（自动 return）
fn add(x, y) => x + y

# 匿名函数
let mul = fn(a, b) => a * b

# 递归
fn fib(n) {
    if n <= 1 { return n }
    return fib(n - 1) + fib(n - 2)
}

# 闭包
fn make_adder(x) => fn(y) => x + y
let add5 = make_adder(5)
print(add5(3))    # 8
```

### 图形编辑

```lpp
let img = create_image(400, 300, "#1a1a2e")
draw_rect(img, 50, 40, 120, 80, "#e94560")
draw_circle(img, 200, 150, 50, "#f5a623")
draw_text(img, 60, 200, "Hello FPLP!", 32, "white")
save_image(img, "output.png")
show_image(img)
```

### 扩展库

```lpp
json.stringify(data, 2)      # 带缩进的 JSON
math.sqrt(144)               # 数学库
os.listdir(".")              # 文件系统
string.repeat("ha", 3)       # 字符串工具
time.strftime("%Y-%m-%d")    # 时间格式化
```

---

## 🏗 项目结构

```
main.py              # 入口（REPL + 文件运行 + GUI）
fplp/
  lexer.py           # 词法分析器
  parser.py          # Pratt 递归下降解析器
  ast_nodes.py       # AST 节点定义
  compiler.py        # AST → 字节码编译器 + 窥孔优化
  vm.py              # 栈式虚拟机
  bytecode.py        # 指令集定义
  environment.py     # 变量作用域
  evaluator.py       # 树遍历解释器（备用）
  builtins.py        # 40+ 内置函数
  graphics.py        # 图形编辑（Pillow）
  libs.py            # 扩展库（json/math/os/string/time）
  block_editor.py    # Scratch 风格积木编辑器
  gui.py             # tkinter 桌面 GUI
examples/            # 示例代码
fplp_icon.png        # 语言图标
fplp.bat             # Windows 快捷启动
```

---

## ⚡ 性能

对比树遍历解释器（执行 demo.fplp 100 次）：

| 引擎 | 时间 | 加速比 |
|------|------|--------|
| 树遍历解释器 | 2.6ms | 1.0x |
| 栈式 VM | 1.5ms | **1.8x** |

优化策略：dispatch table 指令分发、内联 push/pop、环境遍历内联、VM 复用。

---

## 📄 许可证

MIT License
