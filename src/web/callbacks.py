# src/web/callbacks.py
import time
from typing import Any, Dict, List
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.documents import Document
from src.database.repository import ChatLogRepository


class AgentMonitorCallback(BaseCallbackHandler):
    """
    监控 Agent 运行指标并持久化到 SQLite
    """

    def __init__(self):
        self.start_time = 0.0
        self.end_time = 0.0
        self.rag_documents: List[Document] = []
        # 初始化为 0，确保能够进行累加
        self.token_usage = {"input": 0, "output": 0, "total": 0}
        self.tool_calls = []
        self.user_input = ""
        self.error_message = None

    def on_chain_start(
        self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        if not self.start_time:
            self.start_time = time.time()
            if isinstance(inputs, dict):
                self.user_input = inputs.get("input", str(inputs))
            else:
                self.user_input = str(inputs)

    def on_retriever_end(self, documents: List[Document], **kwargs: Any) -> None:
        self.rag_documents.extend(documents)

    def on_tool_end(self, output: str, name: str, **kwargs: Any) -> None:
        self.tool_calls.append(
            {
                "tool": name,
                "result": str(output)[:500],
                "timestamp": time.strftime("%H:%M:%S"),
            }
        )

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """
        核心修复：解析并累加 Token。
        Agent 可能多次调用 LLM，必须累加每一轮的消耗。
        """
        print(f"DEBUG: response.llm_output = {response.llm_output}")

        # 1. 尝试从标准化 metadata 获取 (LangChain 0.2.2+ 推荐)
        # 这是目前最稳妥的方法
        if response.generations:
            for gen_list in response.generations:
                for gen in gen_list:
                    # 检查是否存在标准化的 usage_metadata
                    if hasattr(gen, "message") and hasattr(
                        gen.message, "usage_metadata"
                    ):
                        if gen.message.usage_metadata:
                            self._update_usage(gen.message.usage_metadata)
                            continue  # 如果拿到了就跳过当前 gen 的后续检查

                    # 2. 备选：尝试从 generation_info 获取
                    if gen.generation_info and (
                        "token_usage" in gen.generation_info
                        or "usage" in gen.generation_info
                    ):
                        usage = gen.generation_info.get(
                            "token_usage"
                        ) or gen.generation_info.get("usage")
                        self._update_usage(usage)

        # 3. 备选：从全局 llm_output 获取 (部分旧版适配器)
        if response.llm_output and "token_usage" in response.llm_output:
            self._update_usage(response.llm_output["token_usage"])

    def _update_usage(self, usage: dict):
        """解析不同的字段名并执行累加"""
        # 兼容 prompt_tokens / input_tokens 两种写法
        if not usage:
            return

        # 适配不同的 Key 名（LangChain 标准、OpenAI 标准、各厂家自定）
        input_tokens = (
            usage.get("prompt_tokens")
            or usage.get("input_tokens")
            or usage.get("input")
            or 0
        )
        output_tokens = (
            usage.get("completion_tokens")
            or usage.get("output_tokens")
            or usage.get("output")
            or 0
        )

        # 累加，因为 Agent 会多次调用 LLM
        self.token_usage["input"] += input_tokens
        self.token_usage["output"] += output_tokens
        self.token_usage["total"] += input_tokens + output_tokens

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        self.error_message = str(error)

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        # 只在最外层 Chain 结束时记录时间（避免被子 Chain 重置）
        if "output" in outputs:
            self.end_time = time.time()
            final_output = outputs.get("output", "")
            rag_texts = [doc.page_content[:200] for doc in self.rag_documents]

            try:
                ChatLogRepository.save_log(
                    user_input=self.user_input,
                    ai_output=final_output,
                    latency=self.latency,
                    token_usage=self.token_usage,
                    intermediate_steps=self.tool_calls,
                    rag_sources=rag_texts,
                    status="error" if self.error_message else "success",
                    error_msg=self.error_message,
                )
            except Exception as e:
                print(f"❌ 日志保存失败: {e}")

    @property
    def latency(self) -> float:
        if self.end_time > 0:
            return round(self.end_time - self.start_time, 2)
        return 0.0
