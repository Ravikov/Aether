# Aether — 自循环提示词蒸馏工具

> **⚠️ 开发状态：功能框架搭建**
>
> 本项目仍处于迭代中，API 参数、循环逻辑、输入输出格式都可能发生**不兼容变更**。
> 当前代码以功能验证为主，错误处理和边界情况覆盖尚不完善，请谨慎用于生产环境。

---

## 概述

**Aether** 是一个基于 LLM 自循环自审查机制的提示词蒸馏工具。它通过"生成→模拟→评分→优化"的闭环，自动从原始聊天记录（蒸馏原料）中提炼出系统提示词（system prompt），无需人工反复调参。

### 工作流程

```
输入蒸馏原料 ──→ creat() 生成提示词 + 测试用例
                      │
                      ▼
              simulation_chat() 用该提示词模拟多轮对话
                      │
                      ▼
              check() 将模拟对话与原料对比打分
                      │
          ┌─ 分数达标? ──→ 输出最终提示词到 out/prompt.md
          │
          └─ 否 ──→ 携带修改建议回到 creat() 继续迭代
```

### 核心循环（`core/manager.py`）

| 步骤 | 方法 | 功能 | 采样温度 |
|------|------|------|----------|
| ① 生成 | `creat()` | 根据原料 + 上一轮得分 + 修改建议，生成新版提示词和测试用句 | 0.6 |
| ② 模拟 | `simulation_chat()` | 用新提示词对每条测试用句进行角色扮演对话 | 1.0 |
| ③ 审查 | `check()` | 对比模拟对话与原料，给出总体/类人度/风格相似度评分及修改建议 | 0 |

当 `check()` 给出的总体得分 ≥ 用户设定的分数线时，循环终止。

---

## 快速开始

### 环境要求

- Python ≥ 3.10
- 一个兼容 OpenAI API 的 LLM 端点（默认配置为 DeepSeek API）

### 安装

```bash
# 克隆仓库
git clone <repo-url>
cd Aether

# （推荐）创建虚拟环境
python -m venv .venv
source .venv/bin/activate    # Windows 下使用 .venv\Scripts\activate

# 安装依赖
pip install openai
```

### 配置

编辑 `config/config.json`：

```json
{
    "api": {
        "key": "sk-你的API密钥",
        "url": "https://api.deepseek.com",
        "model": "deepseek-v4-flash"
    }
}
```

> **注意：** `config/config.json` 已在 `.gitignore` 中，不会被提交到版本控制。

### 使用

```bash
python main.py
```

程序会依次提示输入：

1. **蒸馏原料** — 粘贴原始聊天记录（蒸馏对象的对话文本）
2. **蒸馏对象昵称** — 原料中蒸馏对象的称呼/昵称
3. **分数要求** — 期望达到的最低评分（百分制，默认 80）

运行结束后，最终提示词保存在 `out/prompt.md`。

### 中途停止

按 `Ctrl+C` 可安全退出循环，已生成的提示词仍保留在 `out/prompt.md`。

---

## 项目结构

```
Aether/
├── main.py                  # 入口：收集用户输入，启动蒸馏循环
├── common.py                # 全局常量和路径配置
├── core/
│   ├── manager.py           # 蒸馏循环主控制器
│   └── llm_api.py           # LLM API 封装（OpenAI 客户端）
├── config/
│   └── config.json          # API 密钥、URL、模型名称
├── debug/
│   ├── response_debug.py    # 原始 API 响应写入工具
│   ├── response.json        # 最近一次 API 响应（运行时生成）
│   └── record.txt           # 所有 LLM 回复日志（运行时生成）
├── out/
│   └── prompt.md            # 最终蒸馏提示词输出（运行时生成）
├── .gitignore
├── LICENSE                  # MIT
└── README.md
```

---

## 调参说明

在 `common.py` 中有几个可调参数：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `test_time` | `5` | 每轮循环生成的测试用句数量 |
| `score_standard` | `80` | 默认分数线（可由用户输入覆盖） |

在 `core/manager.py` 的 `creat()` 和 `check()` 方法中：

- **`temperature`**：`creat()` = 0.6（生成多样性），`simulation_chat()` = 1.0（对话多样性），`check()` = 0（评分确定性）
- **`max_tokens`**：默认 2048，在 `core/llm_api.py` 的 `touch.__init__()` 中设置

---

## 已知局限 & 优化方向

- [ ] **输入校验**：`main.py` 未对用户输入做校验，空输入或非数字分数可能导致运行时异常
- [ ] **异常处理**：API 请求失败、JSON 解析失败等情况缺少重试机制和友好的错误提示
- [ ] **对话上下文**：`simulation_chat()` 中每条测试用句独立请求，缺乏多轮对话的上下文连贯性
- [ ] **评分稳定性**：`check()` 依赖 LLM 自评分，不同模型/温度下评分标准可能不一致
- [ ] **调试输出**：`response.json` 等调试文件目前硬编码路径，缺少目录初始化检查
- [ ] **循环终止条件**：当前仅以分数达标退出，缺少最大迭代次数保护（无限循环风险）

---