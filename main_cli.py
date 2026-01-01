# main_cli.py
import os

# 禁用 HuggingFace Tokenizers 的并行化，防止死锁和警告
os.environ["TOKENIZERS_PARALLELISM"] = "false"

import warnings
import sys
import traceback
from src.agent.agent_creator import create_port_agent
from src.config import settings

# 忽略一些不必要的警告 (如 LangChain 的 Pydantic 警告)
warnings.filterwarnings("ignore")


def run_cli():
    """
    启动命令行交互界面。
    """
    print(f"🚀 智能口岸通关异常诊断助手已启动！(引擎: {settings.LLM_PROVIDER.upper()})")
    print("=" * 50)
    print("你好，我是AI助手'小宁'。")
    print("你可以问我关于货物状态的问题，例如：")
    print(
        " - '帮我查一下集装箱 NBCT1234567，提单号 BILL002，这票货能赶上‘中远海运金牛座’吗？'"
    )
    print(" - '退出' 或 'exit' 来结束对话。")
    print("=" * 50)

    # --- ✅ 修正：移除硬编码的 OpenAI 检查，改为通用检查 ---
    # 具体的 Key 检查已在 agent_creator 或 settings 中处理
    # 这里只做最基础的拦截
    if settings.LLM_PROVIDER == "zhipu" and not settings.ZHIPUAI_API_KEY:
        print("❌ 错误：未检测到 ZHIPUAI_API_KEY，请检查 .env 文件。")
        return
    elif settings.LLM_PROVIDER == "qwen" and not settings.DASHSCOPE_API_KEY:
        print("❌ 错误：未检测到 DASHSCOPE_API_KEY，请检查 .env 文件。")
        return
    # -------------------------------------------------------

    try:
        # 创建Agent
        print("⚙️  正在初始化 Agent...")
        agent_executor = create_port_agent()
    except Exception as e:
        print(f"❌ 初始化Agent时出错: {e}")
        return

    while True:
        try:
            user_input = input("\n👤 你: ").strip()

            if user_input.lower() in ["退出", "exit", "quit"]:
                print("👋 感谢使用，再见！")
                break

            if not user_input:
                continue

            # 调用Agent并获取响应
            print("\n🤖 小宁正在思考中... (查询数据 & 检索法规)")

            # 使用 invoke 调用 Agent
            response = agent_executor.invoke({"input": user_input})

            print("\n🤖 小宁:")
            print(response["output"])
            print("-" * 50)

        except KeyboardInterrupt:
            print("\n\n👋 用户中断，感谢使用！")
            break
        except Exception as e:
            print(f"❌ 发生了一个错误: {e}")
            print("🔍 错误堆栈详情:")
            traceback.print_exc()  # <--- 关键修改：打印完整堆栈


if __name__ == "__main__":
    """
    uv run python -m main_cli

    query:
    帮我查一下箱号 NBCT1234567，提单号 BILL002。这票货明天能赶上“中远海运金牛座”吗？我很急，一直没放行。
    查一下集装箱 TRLU1234567，提单号 BILL001。船名是“中远海运金牛座”。一切正常吗？
    帮我查个不存在的箱子 ERROR999999，看看什么情况。
    """
    run_cli()
