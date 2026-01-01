# script/build_vector_store.py
import sys
from pathlib import Path

# 将项目根目录加入路径，确保能导入 src
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir))

from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import settings


def build_and_save_vector_store():
    """
    读取知识库文件，生成 Embeddings，并保存 FAISS 索引到本地磁盘。
    """
    print("🚀 开始构建本地向量知识库...")

    # 1. 检查源文件
    kb_path = settings.KNOWLEDGE_BASE_PATH
    if not kb_path.exists():
        print(f"❌ 错误: 找不到知识库源文件: {kb_path}")
        return

    # 2. 加载数据
    print(f"📖 正在读取文档: {kb_path}")
    loader = TextLoader(str(kb_path), encoding="utf-8")
    documents = loader.load()

    # 3. 文本切分
    print("✂️  正在切分文本...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    docs = text_splitter.split_documents(documents)
    print(f"ℹ️  共切分为 {len(docs)} 个片段。")

    # 4. 初始化 Embedding 模型
    print(f"🧠 加载 Embedding 模型 ({settings.EMBEDDING_MODEL_NAME})...")
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)

    # 5. 生成向量索引
    print("⚡ 正在生成向量索引 (FAISS)...")
    vectorstore = FAISS.from_documents(docs, embeddings)

    # 6. 保存到本地
    save_path = settings.VECTOR_STORE_PATH
    # 确保父目录存在
    save_path.parent.mkdir(parents=True, exist_ok=True)

    vectorstore.save_local(str(save_path))

    print(f"✅ 向量库构建成功并已保存至: {save_path}")
    print("💡 提示: 现在运行主程序将直接加载此索引，无需重新构建。")


if __name__ == "__main__":
    """
    uv run python -m script.build_vector_store
    """
    try:
        build_and_save_vector_store()
    except Exception as e:
        print(f"❌ 构建失败: {e}")
