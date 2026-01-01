from datetime import datetime
from typing import List
import sys
import importlib.metadata

# --- 标准导入 ---
try:
    # 尝试导入 AgentExecutor
    # 注意：在 LangChain 0.3+ 中，AgentExecutor 依然位于 langchain.agents
    from langchain.agents import AgentExecutor, create_tool_calling_agent
except ImportError as e:
    print(f"❌ 严重错误: 无法导入 AgentExecutor。")
    print(f"   错误详情: {e}")
    print("   诊断信息:")

    # 使用 importlib.metadata (Python 3.8+) 替代过时的 pkg_resources
    packages_to_check = ["langchain", "langchain-community", "langchain-core"]
    for pkg in packages_to_check:
        try:
            version = importlib.metadata.version(pkg)
            print(f"   ✅ {pkg}: {version}")
        except importlib.metadata.PackageNotFoundError:
            print(f"   ❌ {pkg}: 未安装")

    print("\n   建议操作: 请删除 .venv 文件夹和 uv.lock 文件，然后重新运行 'uv sync'")
    sys.exit(1)

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_community.chat_models import ChatZhipuAI

# from langchain_community.chat_models import ChatTongyi
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI

from src.tools.port_tools import all_tools
from src.rag.retriever_factory import get_rag_tool
from src.config import settings

SYSTEM_PROMPT_TEMPLATE = """
身份定义：
你是“宁波国际物流网”的资深业务专家助手“小宁”。你精通集装箱动态、海关查验流程及船期调度。

当前时间：
{current_time}

核心原则：
1. **数据驱动**：必须优先调用工具获取真实数据（箱号状态、报关状态、船期），**严禁凭空编造**。
2. **知识增强**：一旦发现异常状态（如海关查验、未放行），**必须**调用知识库工具 (`port_regulation_knowledge_base`) 查询具体含义和应对策略。
3. **时效敏感**：在分析船期时，务必对比“当前时间”与“截关时间(CVT)”，计算剩余窗口。

回复格式要求：
请按照以下结构组织回答：
- **🔍 状态核查**：列出查询到的关键数据。
- **🧠 智能诊断**：结合知识库解释状态（例如：H98查验意味着什么？）。
- **💡 行动建议**：给出明确的下一步操作指引（如：联系报关行、申请预漏装）。
"""


class PortAgentFactory:
    def __init__(self, temperature: float = 0.1):
        self.temperature = temperature
        self.tools = self._load_tools()
        self.llm = self._init_llm()

    def _load_tools(self) -> List[BaseTool]:
        return all_tools + [get_rag_tool()]

    def _init_llm(self) -> BaseChatModel:
        provider = settings.LLM_PROVIDER
        if provider == "zhipu":
            return ChatZhipuAI(
                model=settings.ZHIPU_MODEL_NAME,
                api_key=settings.ZHIPUAI_API_KEY,
                temperature=self.temperature,
                # Zhipu 建议关闭流式以获得更稳定的工具调用
                streaming=False,
            )
        elif provider == "qwen":
            return ChatOpenAI(
                model=settings.QWEN_MODEL_NAME,  # 确保这里是 "qwen-turbo" 或 "qwen-max"
                api_key=settings.DASHSCOPE_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 阿里云兼容端点
                temperature=self.temperature,
                streaming=False,  # 即使这里设为 False，ChatOpenAI 也能处理 Agent 强制的 stream 调用
            )
        else:
            raise ValueError(f"❌ Unsupport Provider: {provider}")

    def _build_prompt(self) -> ChatPromptTemplate:
        current_time_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYSTEM_PROMPT_TEMPLATE),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )
        return prompt.partial(current_time=current_time_str)

    def create_executor(self, verbose: bool = True) -> AgentExecutor:
        prompt = self._build_prompt()
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=verbose,
            handle_parsing_errors=True,
            max_iterations=5,
        )


def create_port_agent() -> AgentExecutor:
    factory = PortAgentFactory()
    return factory.create_executor()
