# src/config/settings.py
from pathlib import Path
import os
from dotenv import load_dotenv

# 加载 .env 文件
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# --- 基础路径配置 ---
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_BASE_PATH = DATA_DIR / "knowledge_base.txt"
MOCK_API_DATA_PATH = DATA_DIR / "mock_api_data.json"

# --- RAG / Embedding 配置 ---
# 本地 Embedding 模型 (通用)
EMBEDDING_MODEL_NAME = "m3e-base"


# =======================================================
# --- 大模型 (LLM) 配置 ---
# =======================================================

# 🟢 选择你的 LLM 提供商
# 可选值: "zhipu" (智谱GLM) 或 "qwen" (阿里通义千问)
# 默认优先读取环境变量 LLM_PROVIDER，如果未设置则默认为 "zhipu"
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "zhipu").lower()

# --- 1. 智谱 AI (ChatGLM) 配置 ---
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY")
# 模型选项: "glm-4", "glm-4-plus", "glm-4-flash"
ZHIPU_MODEL_NAME = "glm-4"

# --- 2. 阿里通义千问 (Qwen) 配置 ---
# 使用 Qwen 需要安装 dashscope: pip install dashscope
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY")
# 模型选项: "qwen-plus" (推荐, 性价比高), "qwen-max" (能力最强), "qwen-turbo" (快)
# QWEN_MODEL_NAME = "qwen-plus" 
QWEN_MODEL_NAME = "qwen-turbo" 


# --- 配置检查 (可选) ---
if LLM_PROVIDER == "zhipu" and not ZHIPUAI_API_KEY:
    print("⚠️ 警告: 已选择 zhipu 模式，但未检测到 ZHIPUAI_API_KEY")
elif LLM_PROVIDER == "qwen" and not DASHSCOPE_API_KEY:
    print("⚠️ 警告: 已选择 qwen 模式，但未检测到 DASHSCOPE_API_KEY")