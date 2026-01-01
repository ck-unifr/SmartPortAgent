# src/rag/retriever_factory.py
from pathlib import Path
from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import Tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

from src.config import settings


class RAGRetrieverFactory:
    """
    一个工厂类，负责创建、管理和提供RAG检索器及其对应的LangChain工具。

    这个类被设计为单例模式（通过模块级实例），以确保昂贵的资源
    （如Embedding模型和向量数据库）只被初始化一次。
    """

    def __init__(
        self,
        knowledge_base_path: Path = settings.KNOWLEDGE_BASE_PATH,
        embedding_model_name: str = settings.EMBEDDING_MODEL_NAME,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        search_k: int = settings.SEARCH_K,
    ):
        """
        初始化工厂，加载和处理所有必要的组件。
        """
        print("🔄 正在初始化 RAG 向量知识库 (仅一次)...")
        self.config = {
            "path": knowledge_base_path,
            "embedding": embedding_model_name,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "search_k": search_k,
        }

        # 1. 初始化核心组件
        self.embeddings = HuggingFaceEmbeddings(model_name=self.config["embedding"])
        self.text_splitter = self._create_text_splitter()

        # 2. 构建检索器
        self.retriever = self._create_retriever()
        print("✅ RAG 向量知识库初始化完成。")

    def _create_text_splitter(self) -> TextSplitter:
        """创建文本分割器实例。"""
        return RecursiveCharacterTextSplitter(
            chunk_size=self.config["chunk_size"],
            chunk_overlap=self.config["chunk_overlap"],
        )

    def _load_and_split_documents(self) -> List[Document]:
        """从文件加载并分割文档。"""
        loader = TextLoader(str(self.config["path"]), encoding="utf-8")
        documents = loader.load()
        return self.text_splitter.split_documents(documents)

    def _create_retriever(self) -> BaseRetriever:
        """创建向量数据库和检索器。"""
        docs = self._load_and_split_documents()
        vectorstore = FAISS.from_documents(docs, self.embeddings)
        return vectorstore.as_retriever(search_kwargs={"k": self.config["search_k"]})

    def get_retriever(self) -> BaseRetriever:
        """获取已创建的检索器实例。"""
        return self.retriever

    def get_tool(self) -> Tool:
        """
        将RAG检索器包装成一个Agent可以使用的标准Tool。
        """

        def _retrieve_and_format_docs(query: str) -> str:
            """工具的核心执行逻辑：检索并格式化输出。"""
            docs = self.retriever.invoke(query)
            return "\n\n".join(doc.page_content for doc in docs)

        return Tool(
            name=settings.RETRIEVER_TOOL_NAME,
            description=settings.RETRIEVER_TOOL_DESCRIPTION,
            func=_retrieve_and_format_docs,
        )


# --- 模块级单例 ---
# 在模块加载时创建 RAGRetrieverFactory 的唯一实例。
# 其他模块可以直接导入这个实例使用，无需关心其创建过程。
rag_retriever_factory = RAGRetrieverFactory()


# --- 便捷函数 (可选，但推荐) ---
# 提供与旧代码兼容的简单接口，隐藏工厂实现细节。
def get_rag_retriever() -> BaseRetriever:
    """获取全局RAG检索器实例。"""
    return rag_retriever_factory.get_retriever()


def get_rag_tool() -> Tool:
    """获取全局RAG工具实例。"""
    return rag_retriever_factory.get_tool()
