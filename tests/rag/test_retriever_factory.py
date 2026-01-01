import unittest
import shutil
import tempfile
from pathlib import Path
import sys
import os

# 确保 src 目录在 python path 中，以便能导入模块
# 假设脚本运行在项目根目录或 tests 目录下
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.rag.retriever_factory import RAGRetrieverFactory
from langchain_core.documents import Document


class TestRAGRetrieverFactory(unittest.TestCase):

    def setUp(self):
        """
        在每个测试用例开始前执行：
        创建一个临时的知识库文件，用于测试检索功能。
        """
        # 1. 创建临时目录
        self.test_dir = tempfile.mkdtemp()
        self.test_kb_path = Path(self.test_dir) / "test_knowledge_base.txt"

        # 2. 写入测试数据
        # 模拟一些海关相关的特定内容
        mock_content = (
            "宁波口岸查验流程说明：\n"
            "1. 进口货物需提前24小时申报。\n"
            "2. 查验时必须有报关员在场。\n"
            "3. 如果遇到查验异常，请联系现场海关科室。\n\n"
            "关于危险品运输的规定：\n"
            "所有危险品必须张贴明显的警告标签，并提供MSDS文件。\n"
        )

        with open(self.test_kb_path, "w", encoding="utf-8") as f:
            f.write(mock_content)

        print(f"\n[Setup] 创建临时测试知识库: {self.test_kb_path}")

    def tearDown(self):
        """
        在每个测试用例结束后执行：
        清理临时文件和目录。
        """
        shutil.rmtree(self.test_dir)
        print("[Teardown] 清理临时测试文件完成。")

    def test_factory_initialization_and_search(self):
        """测试：工厂初始化 -> 向量化 -> 检索 的完整流程"""

        print("Testing: 正在初始化 Factory (使用临时文件)...")

        # 1. 初始化 Factory
        # 关键点：我们传入临时的路径，而不是使用 settings 中的默认路径
        # 这样可以隔离环境，确保测试的是逻辑而不是数据
        factory = RAGRetrieverFactory(
            knowledge_base_path=self.test_kb_path,
            chunk_size=100,  # 测试用小一点的切分
            chunk_overlap=10,
            search_k=1,
        )

        # 2. 获取检索器
        retriever = factory.get_retriever()
        self.assertIsNotNone(retriever, "检索器实例不应为空")

        # 3. 测试检索功能
        query = "查验时谁必须在场？"
        print(f"Testing: 执行检索 Query='{query}'")

        results = retriever.invoke(query)

        # 4. 验证结果
        self.assertTrue(len(results) > 0, "检索结果不应为空")
        first_doc = results[0]

        print(f"Testing: 检索结果 -> {first_doc.page_content}")

        # 验证是否检索到了相关内容 (关键词匹配)
        self.assertIn("报关员", first_doc.page_content, "检索结果应包含关键词'报关员'")
        self.assertIsInstance(first_doc, Document, "返回对象应该是 Document 类型")

    def test_tool_creation_and_usage(self):
        """测试：Tool 工具的创建和格式化输出功能"""

        factory = RAGRetrieverFactory(knowledge_base_path=self.test_kb_path, search_k=2)

        # 1. 获取 Tool
        tool = factory.get_tool()

        # 验证 Tool 属性
        self.assertEqual(tool.name, "port_regulation_knowledge_base", "Tool 名称不匹配")
        self.assertTrue(tool.description, "Tool 描述不应为空")

        # 2. 执行 Tool
        query = "危险品"
        print(f"Testing: 执行 Tool Query='{query}'")
        output = tool.func(query)  # 直接调用 func 模拟 Agent 调用

        print(f"Testing: Tool 输出 -> \n{output}")

        # 3. 验证输出格式
        self.assertIsInstance(output, str, "Tool 返回类型必须是字符串")
        self.assertIn("MSDS", output, "Tool 输出应包含知识库中的关键词")


if __name__ == "__main__":
    """ 
    uv run python -m tests.rag.test_retriever_factory
    """
    unittest.main()
