# 🧠 豆语 DouLang

让AI真正记住你 —— 基于7个科学实验验证的AI记忆系统。

## 🚀 一键安装

### 方式1：Python脚本（推荐）

```bash
# 下载并运行安装脚本
curl -sSL https://raw.githubusercontent.com/xiaocaojimmy/doulang/main/install.py | python3

# 或者Windows
python install.py
```

### 方式2：Docker（最简单）

```bash
# 克隆仓库
git clone https://github.com/xiaocaojimmy/doulang.git
cd doulang

# 一键启动
docker-compose up -d

# 完成！访问 http://localhost:3000
```

### 方式3：pip安装

```bash
pip install doulang
```

## ⚡ 5秒快速开始

```python
from doulang import DouLangEnhanced

# 创建实例
dl = DouLangEnhanced()

# 对话（自动记忆）
dl.chat_with_memory("我是科幻小说作者")

# 20轮后...
dl.chat_with_memory("我是谁？")  # 仍然记得！
```

## ✨ 核心特性

- 🎯 **智能优先级** - 身份(1.5) > 偏好(1.0) > 事实(0.3)
- ⏰ **时间感知** - 20轮阈值，自动衰减旧记忆
- 🎭 **自然融入** - 伪装成"对话上下文"，AI自然回复
- 🛡️ **诚实守卫** - 不编造不存在的信息
- 🧹 **自动清理** - 存储上限100条，自动管理
- 🔬 **实验验证** - 基于FMS实验 #0-#7

## 📚 文档

- [完整文档](https://xiaocaojimmy.github.io/fractal-memory-research/)
- [实验报告](https://github.com/xiaocaojimmy/fractal-memory)
- [API参考](./docs/API.md)

## 🤝 贡献

欢迎Issue和PR！

## 📜 许可证

MIT © 2026 小豆 🫘
