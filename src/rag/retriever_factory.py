# src/rag/retriever_factory.py
from functools import lru_cache
from typing import Optional

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import Tool  # ✅ 改用核心库的基础 Tool 类

from src.config import settings


@lru_cache(maxsize=1)
def create_rag_retriever() -> BaseRetriever:
    """
    创建并返回一个配置好的RAG检索器。
    使用 lru_cache 避免每次调用 Tool 时重复进行 Embedding 计算。
    """
    print("🔄 正在初始化 RAG 向量知识库 (仅一次)...")

    # 1. 加载文档
    loader = TextLoader(str(settings.KNOWLEDGE_BASE_PATH), encoding="utf-8")
    documents = loader.load()

    # 2. 切分文档
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )
    docs = text_splitter.split_documents(documents)

    # 3. 初始化Embedding模型
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)

    # 4. 创建向量数据库
    vectorstore = FAISS.from_documents(docs, embeddings)

    # 5. 构建检索器
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})

    print("✅ RAG 向量知识库初始化完成。")
    return retriever


# --- 👇 手动实现 create_retriever_tool 以避开导入错误 ---
def _format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def get_rag_tool():
    """
    将RAG检索器包装成一个Agent可以使用的工具。
    (手动封装模式，不依赖 langchain.tools.retriever)
    """
    retriever = create_rag_retriever()

    # 定义工具的具体执行函数
    def retrieve_and_format(query: str) -> str:
        """检索知识库并返回格式化文本"""
        docs = retriever.invoke(query)
        return _format_docs(docs)

    # 创建标准 Tool 对象
    retriever_tool = Tool(
        name="port_regulation_knowledge_base",
        description="查询宁波口岸的海关规定、查验流程、操作SOP和风险提示。当你需要解释为什么会出现某种海关状态，或者该如何应对时，使用这个工具。",
        func=retrieve_and_format,
    )

    return retriever_tool
