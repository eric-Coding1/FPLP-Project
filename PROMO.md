# FPLP - 自研脚本语言 推广材料

## 🎯 一句话介绍
> 花了一个月自研的脚本语言 FPLP，字节码 VM + 图形编辑 + GUI 积木模式，已开源到 Gitee。欢迎 Star！

---

## 📝 中文推广文案（V2EX / 知乎 / 掘金）

### 标题选项

1. 《我写了一个脚本语言：FPLP，有字节码VM、积木编辑器和pip一样的包管理器》
2. 《自研编程语言 FPLP 开源了！从零实现字节码编译器+栈式虚拟机》
3. 《为了学编译原理，我写了个叫 FPLP 的语言，结果做成了全套工具链》

### 正文

```
大概花了一个多月，从零写了一个轻量级脚本语言 FPLP（Fast Parallel Language Plus）。

初衷是想彻底搞明白"编译器是怎么工作的"，结果一做就停不下来，最后整出了个麻雀虽小五脏俱全的语言：

🔧 技术栈
• Pratt 递归下降解析器
• AST → 字节码编译器（29条指令集）
• 栈式虚拟机（dispatch table 调度）
• 1.8x 加速比 vs 树遍历解释器
• 可转译到 Python 字节码（26x 加速 🚀）

🎨 语言特性
• 动态类型，10个关键字，语法像简化版 JS
• 一等函数、闭包、递归、高阶函数
• 40+ 内置函数（字符串/数学/文件IO/集合）
• 5个扩展库（json/math/os/string/time/http/base64/hashlib/csv/re）
• 18个 Pillow 图形函数（绘制/变换/滤镜）

🖥️ 桌面 GUI
• tkinter 代码编辑器（深色主题、行号）
• 积木模式（Scratch风格，10类54个积木）
• 图片预览面板

📦 包管理
• pip 风格的 fplp install <包名>
• 包自动转译到 Python 原生函数
• 安装即用，无需配置

⚡ 性能
常规模式：1.5ms（vs 2.6ms 树遍历）
加速模式：0.09ms（转译到 Python 字节码）

已开源到 Gitee，欢迎 Star/Fork/PR！
https://gitee.com/eric_Coding/fplp-project
```

---

## 📝 英文推广文案（Reddit / Hacker News / Twitter）

### Headline
**I built a scripting language from scratch: FPLP - bytecode VM, block editor, and pip-like package manager**

### Post

```
After a month of work, I'm releasing FPLP (Fast Parallel Language Plus) - a lightweight scripting language implemented in pure Python.

What started as a "let's understand how compilers work" project turned into a full language toolchain:

🔧 Tech Stack
• Pratt recursive descent parser
• AST → bytecode compiler (29 opcodes)
• Stack-based VM with dispatch table
• 1.8x speedup vs tree-walk interpreter
• Python bytecode transpiler (26x speedup)

🎨 Features
• Dynamic typing, 10 keywords, JS-like syntax
• First-class functions, closures, recursion, HOFs
• 40+ built-in functions
• 60+ extension library functions (json/math/os/http/csv/re/hashlib/base64)
• 18 Pillow graphics functions

💻 GUI
• tkinter code editor (dark theme)
• Scratch-style block editor (10 categories, 54 blocks)
• Image preview panel

📦 Package Manager
• pip-style: fplp install <package>
• Auto-transpile to native Python functions

Open source on Gitee. Star/fork/PR welcome!
https://gitee.com/eric_Coding/fplp-project
```

---

## 📢 推荐发布平台

| 平台 | 适合内容 | 链接 |
|------|---------|------|
| **V2EX** | 程序员社区，发「分享创造」板块 | v2ex.com/go/create |
| **知乎** | 发文章或想法，标签「编程」「开源」 | zhihu.com |
| **掘金** | 技术文章平台 | juejin.cn |
| **B站** | 录个3分钟演示视频更炸 | bilibili.com |
| **Hacker News** | Show HN: 英文版发这里 | news.ycombinator.com |
| **Reddit r/programming** | 英文版 | reddit.com/r/programming |
| **QQ群/微信群** | 编译器/语言设计相关群 | - |

---

## 🚀 可以帮忙做的事情

如果需要，我还可以：
1. ✅ 生成几张酷炫的截图/演示图（showcase 跑出来的结果）
2. ✅ 优化 README 加 CI badge、Star 数等
3. ⏳ 写一个简单的官网页面（HTML）
4. ⏳ 做 GIF 动图演示积木编辑器和 GUI
