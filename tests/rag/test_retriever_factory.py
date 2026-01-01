# tests/test_retriever_factory.py
import sys
import time
from pathlib import Path

# --- 1. 路径设置 (确保能导入 src) ---
current_test_dir = Path(__file__).resolve().parent
project_root = current_test_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.rag.retriever_factory import create_rag_retriever, get_rag_tool
    from src.config import settings
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)


def test_retrieval_accuracy():
    """
    测试检索的准确性：
    输入一个业务问题，检查返回的文档是否包含预期的关键词。
    """
    print("\n🧪 测试 1: 向量检索准确性 (Retrieval Accuracy)")
    print("   (首次运行可能需要下载 Embedding 模型，请耐心等待...)")

    start_time = time.time()
    try:
        retriever = create_rag_retriever()
        load_time = time.time() - start_time
        print(f"   ⏱️  初始化/加载耗时: {load_time:.2f}秒")

        # 测试问题
        query = "H98查验是什么意思？需要多久？"
        print(f"   ❓ 模拟提问: {query}")

        # 执行检索 (LangChain v0.1+ 使用 invoke)
        docs = retriever.invoke(query)

        print(f"   📄 检索到的文档块数量: {len(docs)}")

        if not docs:
            print("   ❌ 未检索到任何文档！请检查 data/knowledge_base.txt 是否有内容。")
            return

        # 验证内容
        first_doc_content = docs[0].page_content
        print("   " + "-" * 40)
        print(f"   📝 最佳匹配内容预览:\n{first_doc_content[:150]}...")
        print("   " + "-" * 40)

        # 关键词断言
        expected_keywords = ["H98", "机检", "X光", "查验"]
        found = [kw for kw in expected_keywords if kw in first_doc_content]

        if found:
            print(f"   ✅ 验证通过: 找到了关键词 {found}")
        else:
            print(
                f"   ⚠️ 警告: 未找到预期关键词 {expected_keywords}，检索效果可能不佳。"
            )

    except Exception as e:
        print(f"   ❌ 检索过程发生错误: {e}")


def test_caching_performance():
    """
    测试 lru_cache 是否生效。
    第二次获取 retriever 应该不需要重新加载模型，耗时应接近 0。
    """
    print("\n🧪 测试 2: 缓存性能测试 (Caching)")

    print("   🔄 第一次调用 (已在测试1中初始化)...")
    t1 = time.time()
    r1 = create_rag_retriever()
    t1_end = time.time()
    print(f"   ⏱️  调用耗时: {t1_end - t1:.4f}秒")

    print("   🔄 第二次调用 (应命中缓存)...")
    t2 = time.time()
    r2 = create_rag_retriever()
    t2_end = time.time()
    duration = t2_end - t2
    print(f"   ⏱️  调用耗时: {duration:.4f}秒")

    if duration < 0.1:
        print("   ✅ 缓存生效 (耗时 < 0.1s)")
    else:
        print("   ⚠️ 缓存似乎未生效 (耗时较长)，请检查 @lru_cache 装饰器。")

    # 验证两次返回的是否是同一个对象
    if r1 is r2:
        print("   ✅ 对象一致性验证通过 (Singleton)")
    else:
        print("   ❌ 对象不一致")


def test_tool_wrapper():
    """
    测试工具包装器是否正确配置。
    """
    print("\n🧪 测试 3: 工具包装 (Tool Wrapper)")
    tool = get_rag_tool()

    print(f"   🛠️  工具名称: {tool.name}")
    print(f"   📝 工具描述: {tool.description[:50]}...")

    if tool.name == "port_regulation_knowledge_base":
        print("   ✅ 工具名称正确")
    else:
        print(f"   ❌ 工具名称错误: {tool.name}")

    if hasattr(tool, "invoke"):
        print("   ✅ 工具具备 invoke 方法 (可被 Agent 调用)")
    else:
        print("   ❌ 工具缺少 invoke 方法")


if __name__ == "__main__":
    """ 
    uv run python -c "import langchain; print(f'LangChain Version: {langchain.__version__}')"
    uv run python -m tests.rag.test_retriever_factory
    
    """
    print("🚀 开始运行 RAG 模块单元测试...")
    print(f"📂 知识库路径: {settings.KNOWLEDGE_BASE_PATH}")
    print("========================================")

    test_retrieval_accuracy()
    test_caching_performance()
    test_tool_wrapper()

    print("\n========================================")
    print("🏁 测试结束")
