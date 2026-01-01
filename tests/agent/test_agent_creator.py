import sys
import unittest
import importlib.metadata
from pathlib import Path

# --- 1. 路径设置 (自动适配项目根目录) ---
# 无论是在项目根目录运行还是在 tests 目录运行，都尝试找到 src
file_path = Path(__file__).resolve()
# 向上寻找包含 pyproject.toml 的目录作为根目录
project_root = file_path.parent
while not (project_root / "pyproject.toml").exists():
    if project_root.parent == project_root:  # 到达根目录
        break
    project_root = project_root.parent

print(f"📂 Project Root detected: {project_root}")
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.config import settings
    from src.agent.agent_creator import PortAgentFactory, create_port_agent
except ImportError as e:
    print(f"❌ 测试脚本导入失败: {e}")
    print(f"   Python Path: {sys.path}")
    sys.exit(1)


class TestAgentCreator(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("\n🔍 Environment Check:")
        try:
            ver = importlib.metadata.version("langchain")
            print(f"   LangChain Version: {ver}")
        except:
            print("   LangChain not found via metadata")

    def test_factory_init(self):
        """测试工厂初始化"""
        print("\n🧪 Test: Factory Initialization")
        factory = PortAgentFactory()
        self.assertIsNotNone(factory.llm)
        print(f"   ✅ LLM Loaded: {type(factory.llm).__name__}")

    def test_tools(self):
        """测试工具加载"""
        print("\n🧪 Test: Tools Loading")
        factory = PortAgentFactory()
        tool_names = [t.name for t in factory.tools]
        self.assertIn("port_regulation_knowledge_base", tool_names)
        print(f"   ✅ Tools count: {len(tool_names)}")

    def test_agent_creation(self):
        """测试 AgentExecutor 创建"""
        print("\n🧪 Test: Agent Executor Creation")
        try:
            agent = create_port_agent()
            self.assertIsNotNone(agent)
            print("   ✅ AgentExecutor created successfully")
        except Exception as e:
            self.fail(f"Agent creation failed: {e}")


if __name__ == "__main__":
    unittest.main()
