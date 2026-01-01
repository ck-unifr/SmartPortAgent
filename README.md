<div align="center">
  <!-- 建议：找一个免费的 AI 生成一个集装箱/港口的卡通 Logo 替换下面的 emoji -->
  <a href="https://github.com/YourUsername/SmartPortAgent">
    <h1>🚢 SmartPortAgent</h1>
  </a>

  <p>
    <strong>智能口岸通关异常诊断助手</strong> <br>
    <i>基于 LLM Agent + RAG 的外贸物流“专家级” copilot</i>
  </p>

  <p>
    <a href="./README_EN.md">English</a> •
    <a href="#-快速开始">快速开始</a> •
    <a href="#-技术架构">技术架构</a> •
    <a href="#-功能演示">功能演示</a>
  </p>

  <!-- 徽章区域 -->
  <p>
    <a href="https://www.python.org/">
      <img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white" alt="Python">
    </a>
    <a href="https://github.com/astral-sh/uv">
      <img src="https://img.shields.io/badge/uv-fastest-purple?logo=python" alt="uv">
    </a>
    <a href="https://python.langchain.com/">
      <img src="https://img.shields.io/badge/LangChain-v0.1-green?logo=chainlink" alt="LangChain">
    </a>
    <br>
    <img src="https://img.shields.io/badge/ZhipuAI-GLM--4-blueviolet" alt="ZhipuAI">
    <img src="https://img.shields.io/badge/Qwen-Turbo%2FMax-ff6a00?logo=alibabacloud&logoColor=white" alt="Qwen">
    <img src="https://img.shields.io/badge/RAG-Enabled-purple" alt="RAG">
    <img src="https://img.shields.io/badge/License-MIT-grey" alt="License">
  </p>

  <!-- 演示 GIF (关键！如果没有，请去录制一个 Streamlit 的操作屏录) -->
  <img src="https://via.placeholder.com/800x450.png?text=Place+Your+Demo+GIF+Here" alt="Demo GIF" width="800">

</div>

---

## 📖 简介

**SmartPortAgent** 是一个专为外贸与物流行业设计的 **AI 智能体 (Agent)** Demo。

它模拟了真实的**智慧口岸**场景，旨在解决外贸人员在货物出口过程中遇到的“数据碎片化”和“异常状态难解读”痛点。通过自然语言对话，Agent 能够自动调度工具查询集装箱、报关和船期状态，并结合内置的**RAG 法律法规知识库**，像一位资深关务专家一样为你诊断异常并提供行动建议。

> **🌟 核心价值**: 输入一个箱号，AI 自动完成 `查询` -> `分析` -> `诊断` -> `建议` 全流程。

## ✨ 核心特性

- **🤖 智能任务规划 (Agent)**: 基于 **LangChain ReAct** 模式，AI 自动思考并并行调用多个模拟 API（如：查询海关状态、查询码头进港信息）。
- **📚 专家级知识库 (RAG)**: 内置宁波口岸查验流程与监管政策，利用 **FAISS + m3e-base** 向量检索，准确解读 "H98"、"查验" 等晦涩术语。
- **🔌 全链路模拟环境**: 包含集装箱生命周期、海关放行状态、船舶截关时间 (CVT) 的完整模拟数据，开箱即用。
- **💡 智能决策风控**: 综合船期截关时间与当前查验进度，自动计算赶船风险，给出“申请预漏装”或“改配”等专业建议。

## 🏗️ 技术架构

```mermaid
graph TD
    User[👤 用户] -->|自然语言提问| Web[🖥️ Streamlit UI]
    Web --> Agent[🤖 LangChain Agent]
    
    subgraph "Core Brain (核心大脑)"
        Agent <-->|推理/规划| LLM[🧠 ZhipuAI/Qwen LLM]
        Agent <-->|工具调用| Tools[🛠️ 工具集合]
    end
    
    subgraph "RAG System (知识增强)"
        Tools -->|检索法规| VectorDB[(🗄️ FAISS 向量库)]
        VectorDB <-->|Embedding| EmbedModel[📉 m3e-base 本地模型]
        VectorDB <-->|加载| KB[📄 知识库 TXT]
    end
    
    subgraph "Mock Infrastructure (模拟设施)"
        Tools -->|API请求| MockData[💾 模拟业务数据 (JSON)]
    end

    Agent -->|最终回复| Web