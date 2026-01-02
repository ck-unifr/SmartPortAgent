# src/agent/agent_creator.py
from datetime import datetime
from typing import List
from typing import List, Optional
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
from langchain_core.callbacks import BaseCallbackHandler
from langchain_community.chat_models import ChatZhipuAI

# from langchain_community.chat_models import ChatTongyi
try:
    from langchain_openai import ChatOpenAI
except ImportError:
    from langchain_community.chat_models import ChatOpenAI

from src.tools.port_tools import all_tools
from src.rag.retriever_factory import get_rag_tool
from src.config import settings
from src.agent.prompts import SYSTEM_PROMPT_TEMPLATE


class PortAgentFactory:
    def __init__(self, temperature: float = 0.001):
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
                # 注意: ChatZhipuAI 默认会在 llm_output 中返回 token_usage
                # 显式禁用搜索工具，防止模型自行搜索互联网干扰 RAG
                model_kwargs={
                    "tools": [{"type": "web_search", "web_search": {"enable": False}}]
                },
            )
        elif provider == "qwen":
            return ChatOpenAI(
                model=settings.QWEN_MODEL_NAME,  # 确保这里是 "qwen-turbo" 或 "qwen-max"
                api_key=settings.DASHSCOPE_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",  # 阿里云兼容端点
                temperature=self.temperature,
                streaming=False,  # 即使这里设为 False，ChatOpenAI 也能处理 Agent 强制的 stream 调用
                # 关键: 强制要求返回 Token 用量 (OpenAI 协议兼容)
                model_kwargs={"stream_options": {"include_usage": True}},
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

    def create_executor(
        self,
        verbose: bool = True,
        callbacks: Optional[List[BaseCallbackHandler]] = None,
    ) -> AgentExecutor:
        """
        创建 Agent 执行器
        :param verbose: 是否打印详细日志
        :param callbacks: 回调列表，用于传递给 Agent 监控 Token 和耗时
        """
        prompt = self._build_prompt()
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=verbose,
            callbacks=callbacks,  # ✅  将监控回调注入到执行器
            handle_parsing_errors=True,
            max_iterations=2,
        )


def create_port_agent() -> AgentExecutor:
    factory = PortAgentFactory()
    return factory.create_executor()
