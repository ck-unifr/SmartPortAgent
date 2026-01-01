# src/rag/retriever_factory.py
from pathlib import Path
from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import tool, BaseTool  # 修改导入
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

from src.config import settings


class RAGRetrieverFactory:
    """
    RAG 检索器工厂类 (单例模式)
    """

    def __init__(
        self,
        knowledge_base_path: Path = settings.KNOWLEDGE_BASE_PATH,
        embedding_model_name: str = settings.EMBEDDING_MODEL_NAME,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        search_k: int = settings.SEARCH_K,
    ):
        print("🔄 正在初始化 RAG 向量知识库 (仅一次)...")
        self.config = {
            "path": knowledge_base_path,
            "embedding": embedding_model_name,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "search_k": search_k,
        }

        self.embeddings = HuggingFaceEmbeddings(model_name=self.config["embedding"])
        self.text_splitter = self._create_text_splitter()
        self.retriever = self._create_retriever()
        print("✅ RAG 向量知识库初始化完成。")

    def _create_text_splitter(self) -> TextSplitter:
        return RecursiveCharacterTextSplitter(
            chunk_size=self.config["chunk_size"],
            chunk_overlap=self.config["chunk_overlap"],
        )

    def _load_and_split_documents(self) -> List[Document]:
        # 增加文件存在性检查
        file_path = Path(self.config["path"])
        if not file_path.exists():
            print(f"⚠️ 警告: 知识库文件未找到: {file_path}")
            return []

        loader = TextLoader(str(file_path), encoding="utf-8")
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def _create_retriever(self) -> BaseRetriever:
        docs = self._load_and_split_documents()

        if not docs:
            print("⚠️ 警告: 知识库为空，加载默认占位符。")
            docs = [
                Document(
                    page_content="暂无相关口岸法规知识。",
                    metadata={"source": "empty_fallback"},
                )
            ]

        vectorstore = FAISS.from_documents(docs, self.embeddings)
        return vectorstore.as_retriever(search_kwargs={"k": self.config["search_k"]})

    def retrieve(self, query: str) -> str:
        """核心检索逻辑，供 Tool 调用"""
        try:
            docs = self.retriever.invoke(query)
            if not docs:
                return "未在知识库中找到相关信息。"
            return "\n\n".join(doc.page_content for doc in docs)
        except Exception as e:
            return f"检索知识库时发生错误: {e}"


# --- 模块级单例 ---
rag_retriever_factory = RAGRetrieverFactory()


# --- ✅ 关键修复：使用 @tool 装饰器定义工具 ---
# 这样能生成标准的 JSON Schema，避免 ChatTongyi/Qwen 解析错误
@tool
def search_port_regulations(query: str) -> str:
    """
    查询宁波口岸的海关查验流程、H98指令含义、人工查验时效及应对策略等法规知识。
    当遇到不清楚的查验状态（如H98）或需要应对建议时，必须调用此工具。
    """
    return rag_retriever_factory.retrieve(query)


def get_rag_tool() -> BaseTool:
    """获取全局RAG工具实例。"""
    return search_port_regulations
