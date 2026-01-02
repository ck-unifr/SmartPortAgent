# src/web/callbacks.py
import time
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.documents import Document


class AgentMonitorCallback(BaseCallbackHandler):
    """
    用于监控 Agent 运行指标的回调处理程序。
    捕获：耗时、Token 消耗、RAG 检索到的文档。
    """

    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.rag_documents: List[Document] = []
        self.token_usage = {"input": 0, "output": 0, "total": 0}
        self.tool_calls = []

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """记录开始时间"""
        if not self.start_time:  # 只记录最外层 Chain 的开始
            self.start_time = time.time()

    def on_retriever_end(self, documents: List[Document], **kwargs: Any) -> None:
        """捕获 RAG 检索到的文档"""
        self.rag_documents.extend(documents)

    def on_tool_end(self, output: str, name: str, **kwargs: Any) -> None:
        """记录工具调用情况"""
        self.tool_calls.append(
            {"tool": name, "result": output[:200] + "..."}
        )  # 截断显示

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """尝试从 LLM 响应中提取 Token 使用情况"""
        # 注意：不同模型提供商 (Zhipu/Qwen/OpenAI) 的 metadata 结构可能不同
        # 这里做一个通用的提取尝试
        if response.llm_output:
            usage = response.llm_output.get("token_usage", {})
            if usage:
                self.token_usage["input"] += usage.get("prompt_tokens", 0) or usage.get(
                    "input_tokens", 0
                )
                self.token_usage["output"] += usage.get(
                    "completion_tokens", 0
                ) or usage.get("output_tokens", 0)
                self.token_usage["total"] += usage.get("total_tokens", 0)

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """记录结束时间"""
        self.end_time = time.time()

    @property
    def latency(self) -> float:
        return round(self.end_time - self.start_time, 2)
