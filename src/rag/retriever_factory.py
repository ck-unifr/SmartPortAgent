# src/rag/retriever_factory.py
import os
from pathlib import Path
from typing import List

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.tools import tool, BaseTool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, TextSplitter

from src.config import settings


class RAGRetrieverFactory:
    """
    RAG 检索器工厂类 (单例模式)
    支持加载本地预构建的向量库，提升启动速度。
    """

    def __init__(
        self,
        knowledge_base_path: Path = settings.KNOWLEDGE_BASE_PATH,
        vector_store_path: Path = settings.VECTOR_STORE_PATH,
        embedding_model_name: str = settings.EMBEDDING_MODEL_NAME,
        chunk_size: int = settings.CHUNK_SIZE,
        chunk_overlap: int = settings.CHUNK_OVERLAP,
        search_k: int = settings.SEARCH_K,
    ):
        print("🔄 正在初始化 RAG 服务...")
        self.config = {
            "kb_path": knowledge_base_path,
            "vs_path": vector_store_path,
            "embedding": embedding_model_name,
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "search_k": search_k,
        }

        # 1. 初始化 Embedding (必须，无论是加载还是构建都需要)
        self.embeddings = HuggingFaceEmbeddings(model_name=self.config["embedding"])

        # 2. 获取向量库 (优先加载本地)
        self.vectorstore = self._get_vectorstore()

        # 3. 创建检索器
        self.retriever = self.vectorstore.as_retriever(
            search_kwargs={"k": self.config["search_k"]}
        )
        print("✅ RAG 检索器准备就绪。")

    def _get_vectorstore(self) -> FAISS:
        """
        获取向量库实例：
        1. 尝试从本地磁盘加载 (速度快)。
        2. 如果本地不存在，则回退到从源文件内存构建 (速度慢)。
        """
        vs_path = self.config["vs_path"]

        # 策略 A: 尝试加载本地索引
        if vs_path.exists() and (vs_path / "index.faiss").exists():
            try:
                print(f"📂 发现本地向量库，正在加载: {vs_path}")
                return FAISS.load_local(
                    str(vs_path),
                    self.embeddings,
                    # ✅ 必须设置为 True 以允许加载本地 pickle 文件 (安全信任本地文件)
                    allow_dangerous_deserialization=True,
                )
            except Exception as e:
                print(f"⚠️ 加载本地向量库失败 ({e})，将回退到重新构建...")

        # 策略 B: 回退到内存构建
        print("🔨 本地索引不可用，正在从源文件构建向量库...")
        return self._build_from_source()

    def _build_from_source(self) -> FAISS:
        """从原始文本构建向量库 (耗时操作)"""
        file_path = self.config["kb_path"]

        if not file_path.exists():
            print(f"⚠️ 严重警告: 知识库源文件未找到: {file_path}")
            # 返回空库防止报错
            empty_doc = Document(
                page_content="暂无知识库数据。", metadata={"source": "empty"}
            )
            return FAISS.from_documents([empty_doc], self.embeddings)

        # 加载与切分
        loader = TextLoader(str(file_path), encoding="utf-8")
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config["chunk_size"],
            chunk_overlap=self.config["chunk_overlap"],
        )
        docs = text_splitter.split_documents(documents)

        # 构建索引
        return FAISS.from_documents(docs, self.embeddings)

    def retrieve(self, query: str) -> str:
        """核心检索逻辑"""
        try:
            docs = self.retriever.invoke(query)
            if not docs:
                return "未在知识库中找到相关信息。"
            return "\n\n".join(doc.page_content for doc in docs)
        except Exception as e:
            return f"检索知识库时发生错误: {e}"


# --- 模块级单例 ---
rag_retriever_factory = RAGRetrieverFactory()


@tool
def search_port_regulations(query: str) -> str:
    """
    查询宁波口岸的海关查验流程、H98指令含义、人工查验时效及应对策略等法规知识。
    当遇到不清楚的查验状态（如H98）或需要应对建议时，必须调用此工具。
    """
    return rag_retriever_factory.retrieve(query)


def get_rag_tool() -> BaseTool:
    return search_port_regulations
