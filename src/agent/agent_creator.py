# src/agent/agent_creator.py
from datetime import datetime
from typing import List, Optional

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import BaseTool
from langchain_core.language_models.chat_models import BaseChatModel

# 模型实现类
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.chat_models import ChatTongyi 

from src.tools.port_tools import all_tools
from src.rag.retriever_factory import get_rag_tool
from src.config import settings

# --- 1. 定义更专业的系统提示词模板 ---
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
    """
    智能口岸 Agent 工厂类
    负责组装 LLM、Tools 和 Prompt，生产可执行的 AgentExecutor。
    """

    def __init__(self, temperature: float = 0.1):
        self.temperature = temperature
        self.tools = self._load_tools()
        self.llm = self._init_llm()

    def _load_tools(self) -> List[BaseTool]:
        """加载所有可用工具（包括业务查询工具和RAG工具）"""
        # 将 RAG 工具动态加入工具列表
        return all_tools + [get_rag_tool()]

    def _init_llm(self) -> BaseChatModel:
        """根据配置初始化具体的 LLM 实例"""
        provider = settings.LLM_PROVIDER
        
        if provider == "zhipu":
            return ChatZhipuAI(
                model=settings.ZHIPU_MODEL_NAME,
                api_key=settings.ZHIPUAI_API_KEY,
                temperature=self.temperature,
            )
        
        elif provider == "qwen":
            return ChatTongyi(
                model=settings.QWEN_MODEL_NAME,
                api_key=settings.DASHSCOPE_API_KEY,
                temperature=self.temperature,
                # 通义千问通常不需要特殊的 search 配置即可支持 tool calling
            )
        
        else:
            raise ValueError(f"❌ 配置错误: 不支持的 LLM 提供商 '{provider}'。请检查 settings.py 或 .env")

    def _build_prompt(self) -> ChatPromptTemplate:
        """构建增强版 Prompt，注入动态时间上下文"""
        
        # 获取当前格式化时间 (物流场景对时间非常敏感)
        current_time_str = datetime.now().strftime("%Y年%m月%d日 %H:%M")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT_TEMPLATE),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # 部分填充 Prompt (Partial formatting) 以注入时间
        return prompt.partial(current_time = current_time_str)

    def create_executor(self, verbose: bool = True) -> AgentExecutor:
        """创建并返回 Agent 执行器"""
        prompt = self._build_prompt()
        
        # 使用 LangChain 标准工厂方法创建 Agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent, 
            tools=self.tools, 
            verbose=verbose,
            handle_parsing_errors=True, # 增强鲁棒性，自动修正简单的解析错误
            max_iterations=5,           # 防止死循环
        )

# --- 对外暴露的便捷函数 ---

def create_port_agent() -> AgentExecutor:
    """
    为了保持向后兼容性（Main.py 调用），保留此便捷函数。
    它实例化工厂并返回执行器。
    """
    factory = PortAgentFactory()
    return factory.create_executor()