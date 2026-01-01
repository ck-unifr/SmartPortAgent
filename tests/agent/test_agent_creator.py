# tests/test_agent_creator.py
import sys
import os
from pathlib import Path
from datetime import datetime

# --- 1. 路径设置 (确保能导入 src) ---
current_test_dir = Path(__file__).resolve().parent
project_root = current_test_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.config import settings

    # 导入我们要测试的类和函数
    from src.agent.agent_creator import PortAgentFactory, create_port_agent
    from langchain_core.prompts import ChatPromptTemplate
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


def test_factory_initialization():
    """测试工厂类的初始化和 LLM 选择逻辑"""
    print("\n🧪 测试 1: 工厂类初始化与配置读取")

    try:
        factory = PortAgentFactory()
        print("   ✅ PortAgentFactory 实例化成功")

        # 验证 LLM 类型
        llm_type = type(factory.llm).__name__
        provider = settings.LLM_PROVIDER

        print(f"   ℹ️  配置文件设置 Provider: {provider}")
        print(f"   ℹ️  实际加载 LLM 类名: {llm_type}")

        if provider == "zhipu" and "Zhipu" in llm_type:
            print("   ✅ LLM 类型匹配正确 (Zhipu)")
        elif provider == "qwen" and "Tongyi" in llm_type:
            print("   ✅ LLM 类型匹配正确 (Qwen/Tongyi)")
        else:
            print(f"   ⚠️ 警告: LLM 类型可能不匹配，请检查 settings.py")

    except Exception as e:
        print(f"   ❌ 工厂初始化失败: {e}")
        # 如果是因为缺 Key 报错，提示用户
        if "key" in str(e).lower():
            print("      (提示: 请检查 .env 文件是否配置了对应的 API Key)")


def test_tool_loading():
    """测试工具是否正确加载"""
    print("\n🧪 测试 2: 工具集加载")
    factory = PortAgentFactory()
    tools = factory.tools

    print(f"   ℹ️  加载工具数量: {len(tools)}")

    # 预期工具名称列表
    expected_tools = [
        "get_container_status",
        "get_customs_status",
        "get_vessel_schedule",
        "port_regulation_knowledge_base",  # RAG 工具
    ]

    tool_names = [t.name for t in tools]
    missing = [t for t in expected_tools if t not in tool_names]

    if not missing:
        print("   ✅ 所有预期工具均已加载")
    else:
        print(f"   ❌ 缺失工具: {missing}")
        print(f"      当前工具: {tool_names}")


def test_prompt_injection():
    """测试 Prompt 是否注入了动态时间"""
    print("\n🧪 测试 3: Prompt 构建与时间注入")
    factory = PortAgentFactory()

    # 调用内部方法生成 Prompt
    prompt_template = factory._build_prompt()

    # 渲染 System Message (模拟运行时的行为)
    # 这里的 input 是假的，只是为了触发 partial formatting
    messages = prompt_template.invoke({"input": "test", "agent_scratchpad": []})
    system_msg = messages.to_messages()[0].content

    print("   ℹ️  System Prompt 片段预览:")
    print("   " + "-" * 40)
    # 打印前 200 个字符
    print(f"   {system_msg[:200]}...")
    print("   " + "-" * 40)

    # 验证是否包含当前年份 (例如 '2025' 或 '2026')
    current_year = datetime.now().strftime("%Y")
    if current_year in system_msg:
        print(f"   ✅ 时间注入成功 (检测到年份 '{current_year}')")
    else:
        print(f"   ❌ 未检测到当前年份，时间注入可能失败")


def test_executor_creation():
    """测试最终 AgentExecutor 的创建"""
    print("\n🧪 测试 4: AgentExecutor 创建 (集成测试)")
    try:
        # 这是 main.py 调用的接口
        agent_executor = create_port_agent()
        print("   ✅ create_port_agent() 调用成功")
        print(f"   ℹ️  Executor 对象: {agent_executor}")
    except Exception as e:
        print(f"   ❌ Executor 创建失败: {e}")


if __name__ == "__main__":
    print("🚀 开始运行 Agent Creator 单元测试...")
    print("========================================")

    test_factory_initialization()
    test_tool_loading()
    test_prompt_injection()
    test_executor_creation()

    print("\n========================================")
    print("🏁 测试结束")
