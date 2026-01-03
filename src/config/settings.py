# src/config/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

# 1. 加载 .env 文件
# 建议使用 resolve() 确保路径是绝对路径
env_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# --- 基础路径配置 ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# 知识库文件路径
KNOWLEDGE_BASE_PATH = DATA_DIR / "knowledge_base.txt"
MOCK_API_DATA_PATH = DATA_DIR / "mock_api_data.json"

# =======================================================
# --- RAG (检索增强生成) 配置 ---
# =======================================================

# 1. Embedding 模型路径 (支持本地路径或 HuggingFace ID)
# 如果本地模型不存在，建议使用默认的在线模型 ID，例如: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_local_model_path = BASE_DIR / "model" / "m3e-base"
EMBEDDING_MODEL_NAME = (
    str(_local_model_path)
    if _local_model_path.exists()
    else "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 2. 文本切分参数 (Text Splitter)
CHUNK_SIZE = 500  # 每个文档块的字符长度
CHUNK_OVERLAP = 50  # 文档块之间的重叠字符数 (防止上下文丢失)

# 3. 检索参数 (Retriever)
SEARCH_K = 2  # 每次检索返回的最相关文档数量

# 4. 工具定义 (Tool)
# Agent 使用这个名字和描述来决定何时调用此工具
RETRIEVER_TOOL_NAME = "port_regulation_knowledge_base"
RETRIEVER_TOOL_DESCRIPTION = (
    "查询宁波口岸的海关规定、查验流程、操作SOP和风险提示。"
    "当你需要解释为什么会出现某种海关状态，或者该如何应对时，使用这个工具。"
)

VECTOR_STORE_PATH: Path = Path("data/vector_store_index")

# 数据库路径
DB_PATH = BASE_DIR / "data" / "port_agent.db"
# 自动创建 data 目录（防止因目录不存在导致 SQLite 报错）
if not os.path.exists(DB_PATH.parent):
    os.makedirs(DB_PATH.parent, exist_ok=True)

# =======================================================
# --- 大模型 (LLM) 配置 ---
# =======================================================

# 🟢 选择你的 LLM 提供商
# 可选值: "zhipu" (智谱GLM) 或 "qwen" (阿里通义千问)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "qwen").lower()

# --- 1. 智谱 AI (ChatGLM) 配置 ---
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
# 模型选项: "glm-4", "glm-4-plus", "glm-4-flash"
ZHIPU_MODEL_NAME = "glm-4"

# --- 2. 阿里通义千问 (Qwen) 配置 ---
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
# 模型选项: "qwen-plus" (推荐), "qwen-max" (最强), "qwen-turbo" (最快/便宜)
QWEN_MODEL_NAME = "qwen-turbo"
# QWEN_MODEL_NAME = "qwen-plus"

# --- 配置检查 (仅在直接运行此文件或初始化时提示) ---
if __name__ != "__main__":
    # 简单的运行时检查，防止 Key 缺失导致后续报错
    if LLM_PROVIDER == "zhipu" and not ZHIPUAI_API_KEY:
        print("⚠️  [Config Warning] 已选择 zhipu 模式，但未检测到 ZHIPUAI_API_KEY")
    elif LLM_PROVIDER == "qwen" and not DASHSCOPE_API_KEY:
        print("⚠️  [Config Warning] 已选择 qwen 模式，但未检测到 DASHSCOPE_API_KEY")
