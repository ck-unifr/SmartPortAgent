# check_env.py
import sys
import os
from pathlib import Path

# 将当前目录加入 Python 路径，确保能导入 src 模块
sys.path.append(str(Path(__file__).resolve().parent))

try:
    from src.config import settings
except ImportError as e:
    print("❌ 导入错误: 无法导入 'src.config.settings'")
    print(f"详细信息: {e}")
    print("请确保你在项目根目录下运行此脚本 (例如: python check_env.py)")
    sys.exit(1)

def mask_key(key: str) -> str:
    """对 API Key 进行脱敏处理"""
    if not key:
        return "❌ 未设置 (Not Set)"
    if len(key) < 10:
        return "****"
    return f"{key[:6]}......{key[-4:]} (长度: {len(key)})"

def check_file(path: Path) -> str:
    """检查文件是否存在"""
    if path.exists():
        return f"✅ 存在 ({path.name})"
    else:
        return f"❌ 不存在! (路径: {path})"

def run_diagnostics():
    print("\n🔍 SmartPortAgent 配置诊断工具")
    print("==================================================")

    # --- 1. 基础路径检查 ---
    print("\n[1] 文件系统与路径检查")
    print(f"   - 项目根目录: {settings.BASE_DIR}")
    print(f"   - 知识库文件: {check_file(settings.KNOWLEDGE_BASE_PATH)}")
    print(f"   - 模拟数据表: {check_file(settings.MOCK_API_DATA_PATH)}")

    # --- 2. 模型提供商配置 ---
    print("\n[2] 大模型 (LLM) 配置状态")
    provider = settings.LLM_PROVIDER
    
    # 颜色高亮当前选中的模式
    if provider == "zhipu":
        current_mode = "🟢 智谱 AI (ChatGLM)"
    elif provider == "qwen":
        current_mode = "🔵 通义千问 (Qwen)"
    else:
        current_mode = f"🔴 未知/不支持 ({provider})"

    print(f"   - 当前模式 (LLM_PROVIDER): {current_mode}")

    # 检查具体模型的 Key
    print(f"\n   --- 智谱 AI 配置详情 ---")
    print(f"   - 模型名称: {settings.ZHIPU_MODEL_NAME}")
    print(f"   - API Key : {mask_key(settings.ZHIPUAI_API_KEY)}")
    if provider == "zhipu" and not settings.ZHIPUAI_API_KEY:
        print("     ⚠️  警告: 当前选择了 zhipu 模式，但未检测到 Key！程序无法运行。")

    print(f"\n   --- 通义千问 配置详情 ---")
    print(f"   - 模型名称: {settings.QWEN_MODEL_NAME}")
    print(f"   - API Key : {mask_key(settings.DASHSCOPE_API_KEY)}")
    if provider == "qwen" and not settings.DASHSCOPE_API_KEY:
        print("     ⚠️  警告: 当前选择了 qwen 模式，但未检测到 Key！程序无法运行。")

    # --- 3. Embedding 配置 ---
    print("\n[3] Embedding (RAG) 配置")
    print(f"   - 本地模型: {settings.EMBEDDING_MODEL_NAME}")

    print("\n==================================================")
    
    # --- 4. 最终总结 ---
    if (provider == "zhipu" and settings.ZHIPUAI_API_KEY) or \
       (provider == "qwen" and settings.DASHSCOPE_API_KEY):
        print("✅ 配置检查通过！你应该可以正常运行 python main.py 了。")
    else:
        print("❌ 配置检查未通过，请检查 .env 文件。")

if __name__ == "__main__":
    """ 
    uv run python -m tests.check_env
    """
    run_diagnostics()