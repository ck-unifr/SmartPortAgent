
# SmartPortAgent | 智能口岸通关异常诊断助手

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![uv](https://img.shields.io/badge/uv-fastest-purple?logo=python)
![LangChain](https://img.shields.io/badge/LangChain-v0.1-green?logo=chainlink)
![ZhipuAI](https://img.shields.io/badge/ZhipuAI-GLM--4-blueviolet)
![RAG](https://img.shields.io/badge/RAG-Enabled-purple)
![License](https://img.shields.io/badge/License-MIT-grey)

**SmartPortAgent** 是一个基于 **LLM Agent (大模型智能体)** 和 **RAG (检索增强生成)** 技术构建的 Demo 项目。

它模拟了**（智慧口岸）**的业务场景，旨在解决外贸人员在货物出口过程中遇到的“数据碎片化”和“异常状态难解读”的问题。通过自然语言对话，Agent 能够自动查询集装箱、报关和船期状态，结合法规知识库诊断异常（如海关查验），并提供专业的行动建议。

---

## 🎯 业务场景与痛点

外贸业务员在出口货物时常遇到以下问题：
*   **信息分散**：需要分别登录码头、海关、船公司网站查询状态。
*   **状态晦涩**：看到“H98 查验”等代码，不懂具体含义和预计耗时。
*   **决策困难**：不知道当前状态下，货物是否还能赶上明天的船。

**本项目的解决方案**：用户只需给出一个箱号或提单号，AI 助手即可自动完成“查询-诊断-建议”的全流程。

## ✨ 核心特性

*   **🤖 智能任务规划 (Agent)**: 基于 LangChain 的 ReAct 模式，自动规划并调用多个查询工具（模拟 API）。
*   **📚 专家知识库 (RAG)**: 内置宁波口岸海关查验流程与监管政策，通过向量检索（FAISS）准确解释业务状态。
*   **🔌 模拟业务接口**: 包含集装箱状态、报关放行状态、船舶截关时间等全链路模拟数据。
*   **💡 智能决策支持**: 综合船期截关时间（CVT）与当前查验进度，计算赶船风险并给出操作建议（如“申请预漏装”）。

## 🛠️ 技术架构

*   **开发语言**: Python 3.10+
*   **核心框架**: LangChain
*   **大语言模型**: OpenAI GPT-4o / GPT-3.5
*   **向量数据库**: FAISS (本地运行)
*   **Embedding**: HuggingFace (m3e-base)

## 📂 项目结构

```text
SmartPortAgent/
├── data/                    # 数据层
│   ├── knowledge_base.txt   # RAG 知识库源文件 (口岸政策/SOP)
│   └── mock_api_data.json   # 模拟 API 的后端业务数据
├── src/                     # 核心代码层
│   ├── agent/               # Agent 构建与 Prompt 定义
│   ├── config/              # 全局配置 (环境、路径)
│   ├── rag/                 # RAG 检索器工厂
│   └── tools/               # 模拟查询工具 (Tools)
├── .env.example             # 环境变量配置模版
├── main.py                  # CLI 启动入口
└── requirements.txt         # 依赖列表
```

## 🚀 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/YourUsername/SmartPortAgent.git
cd SmartPortAgent
```

### 2. 环境准备
建议使用 Conda 或 venv 创建虚拟环境。
```bash
# 创建并激活虚拟环境
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置密钥
将 `.env.example` 复制为 `.env`，并填入你的 OpenAI API Key。
```bash
cp .env.example .env
```
在 `.env` 文件中：
```ini
ZHIPUAI_API_KEY="your_api_key_here"
```

### 4. 运行 Demo
```bash
python main_cli.py
```

### 5. 安装与运行 (使用 uv)

确保你已安装 uv。如果没有，请先运行：
`curl -LsSf https://astral.sh/uv/install.sh | sh` (macOS/Linux) 或参考官方文档。

```bash
# 1. 初始化环境并同步依赖 (自动下载 Python 3.11 和所有依赖)
uv sync

# 2. 运行 Demo
uv run main.py
```

## 💬 使用示例

启动后，您可以输入如下测试指令（基于内置的模拟数据）：

**输入:**
> "帮我查一下集装箱 NBCT1234567，提单号是 BILL002，这票货明天能赶上‘中远海运金牛座’这艘船吗？现在一直没显示放行，我很急。"

**Agent 输出预览:**
> **智能诊断报告**
>
> 1.  **状态诊断**:
>     *   集装箱：已进港 (宁波北仑三期)
>     *   报关状态：**查验 (代码 H98)**
>     *   船期：明日 14:00 截关 (风险极高)
>
> 2.  **智能分析**:
>     *   根据知识库，H98 指令通常代表机检。如果机检图像正常，4-6 小时可放行；若转人工查验需 1-2 工作日。
>
> 3.  **行动建议**:
>     *   立即联系报关行确认是否收到移箱通知。
>     *   鉴于离截关不足 24 小时，建议立即申请“预漏装”以保留下一水船期舱位。

## ⚠️ 免责声明

本项目仅为 **技术演示 (Demo)**，用于展示 LLM Agent 在物流领域的应用潜力。
*   项目中的所有数据（箱号、船期、状态）均为**模拟数据**。
*   本项目**未连接**任何真实的港口或海关生产系统。

## 📄 License

MIT License

## 附录:
### 使用 uv 的步骤与命令

假设你已经位于 `SmartPortAgent` 文件夹下。

#### 第一步：安装 uv (如果尚未安装)
```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 第二步：初始化项目
这将创建 `pyproject.toml` 文件（现代 Python 项目标准配置）。

```bash
uv init
```

#### 第三步：指定 Python 版本
我们显式指定使用 Python 3.11 以确保兼容性。`uv` 会自动为你下载并管理这个版本的 Python，不会污染你的系统环境。

```bash
uv python pin 3.11
```

#### 第四步：添加依赖
我们将 `requirements.txt` 中的依赖迁移到 `uv` 管理。

```bash
# 添加核心依赖
uv add langchain langchain-core langchain-community langchain-huggingface zhipuai python-dotenv

# 添加 AI 计算库 (这些库对版本敏感)
uv add faiss-cpu sentence-transformers
```
*执行完上述命令后，`uv` 会自动创建 `.venv` 虚拟环境并安装好所有包。*

#### 第五步：运行项目
使用 `uv run` 可以自动加载虚拟环境和 `.env` 变量（uv 0.4+ 支持自动加载 .env，如果不生效可手动加载）。

```bash
uv run main_cli.py
```