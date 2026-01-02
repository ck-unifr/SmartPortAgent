import time
from typing import Any, Dict, List, Optional
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.documents import Document


class AgentMonitorCallback(BaseCallbackHandler):
    """
    用于监控 Agent 运行指标的回调处理程序。
    修复了 Token 统计在不同模型间不兼容的问题。
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
        if not self.start_time:
            self.start_time = time.time()

    def on_retriever_end(self, documents: List[Document], **kwargs: Any) -> None:
        self.rag_documents.extend(documents)

    def on_tool_end(self, output: str, name: str, **kwargs: Any) -> None:
        self.tool_calls.append({"tool": name, "result": str(output)[:200] + "..."})

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """
        多重解析策略提取 Token 使用量
        """
        # 策略 A: 从全局 llm_output 提取 (传统 OpenAI 模式)
        if response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            self._update_usage(usage)
            return

        # 策略 B: 从 Generations 里的 message.usage_metadata 提取 (LangChain 0.3+ 标准化路径)
        # 这是解决 Qwen/Zhipu 统计为 0 的关键
        try:
            for generations in response.generations:
                for generation in generations:
                    # 检查是否有标准化 usage_metadata
                    if hasattr(generation, "message") and hasattr(
                        generation.message, "usage_metadata"
                    ):
                        meta = generation.message.usage_metadata
                        if meta:
                            self.token_usage["input"] += meta.get("input_tokens", 0)
                            self.token_usage["output"] += meta.get("output_tokens", 0)
                            self.token_usage["total"] += meta.get("total_tokens", 0)

                    # 某些版本智谱/通义可能放在 additional_kwargs
                    elif (
                        hasattr(generation, "message")
                        and "token_usage" in generation.message.additional_kwargs
                    ):
                        usage = generation.message.additional_kwargs["token_usage"]
                        self._update_usage(usage)
        except Exception as e:
            print(f"DEBUG: Token 解析失败: {e}")

    def _update_usage(self, usage: Dict):
        """通用更新逻辑"""
        self.token_usage["input"] += (
            usage.get("prompt_tokens", 0) or usage.get("input_tokens", 0) or 0
        )
        self.token_usage["output"] += (
            usage.get("completion_tokens", 0) or usage.get("output_tokens", 0) or 0
        )
        self.token_usage["total"] += usage.get("total_tokens", 0) or 0

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        self.end_time = time.time()

    @property
    def latency(self) -> float:
        if self.end_time > 0:
            return round(self.end_time - self.start_time, 2)
        return 0.0
