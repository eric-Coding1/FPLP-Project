# Contributing to FPLP

感谢你对 FPLP 项目的兴趣！以下是参与贡献的方式。

## 🐛 报告 Bug

请在 [Issues](https://gitee.com/eric_Coding/fplp-project/issues) 提交，包含：
- FPLP 版本
- 运行环境（OS, Python 版本）
- 最小复现代码
- 期望结果 vs 实际结果

## 💡 功能建议

同样通过 [Issues](https://gitee.com/eric_Coding/fplp-project/issues) 提交，标签选 `enhancement`。

## 🔧 提交 PR

1. Fork 本仓库
2. 创建分支：`git checkout -b feature/your-feature`
3. 提交改动
4. 推送到你的仓库：`git push origin feature/your-feature`
5. 提交 Pull Request

### 代码规范
- Python 代码遵循 PEP 8
- FPLP 语法保持简洁（10 关键字风格）
- 新增内置函数需在 `fplp/builtins.py` 注册
- 新增扩展库需在 `fplp/libs.py` 注册

### 开发指南
```bash
# 克隆
git clone https://gitee.com/eric_Coding/fplp-project.git
cd fplp-project

# 运行
python main.py                    # GUI 模式
python main.py --cli demo.fplp    # CLI 模式
python main.py --py demo.fplp     # 加速模式

# 测试所有示例
for f in examples/*.fplp; do python main.py --cli "$f"; done
```

## 📦 创建包

包是一个 `.fplp` 文件，安装到 `~/.fplp/packages/` 后自动加载。

格式示例：
```lpp
# my-package: 简短描述

fn hello() {
    print("Hello from my package!")
}

fn add(x, y) => x + y
```

欢迎提交包到 [fplp-packages](https://gitee.com/eric_Coding/fplp-packages) 注册表！

## 📄 协议

本项目使用 MIT License。
