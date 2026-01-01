# tests/tools/test_port_tools.py
import sys
import pytest
from unittest.mock import patch
from pathlib import Path

# --- 1. 路径设置 (确保能导入 src) ---
current_test_dir = Path(__file__).resolve().parent
project_root = current_test_dir.parent.parent  # 指向根目录
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from src.tools.port_tools import (
        get_container_status,
        get_customs_status,
        get_vessel_schedule,
        all_tools,
    )
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# --- 2. 准备测试用的伪造数据 (Mock Data) ---
# 这样测试就不依赖于真实的 json 文件，更加稳定
MOCK_DB_DATA = {
    "containers": {
        "TEST_BOX_001": {
            "container_id": "TEST_BOX_001",
            "status": "已进港",
            "location": "测试堆场A",
        }
    },
    "customs": {
        "TEST_BL_001": {"bill_of_lading": "TEST_BL_001", "customs_status": "放行"}
    },
    "vessels": {
        "测试轮": {
            "vessel_name": "测试轮",
            "voyage": "V001",
            "customs_clearance_deadline": "2026-12-31",
        }
    },
}

# --- 3. 测试用例 ---


@patch("src.tools.port_tools._load_mock_data", return_value=MOCK_DB_DATA)
def test_get_container_status(mock_load):
    """测试集装箱查询工具"""
    print("\n🧪 测试: get_container_status")

    # 场景 1: 查询存在的箱号
    # 注意: LangChain tool 使用 .invoke() 调用
    result_exist = get_container_status.invoke("TEST_BOX_001")
    assert result_exist["status"] == "已进港"
    assert result_exist["location"] == "测试堆场A"
    print("   ✅ 正常数据查询通过")

    # 场景 2: 查询不存在的箱号
    result_missing = get_container_status.invoke("MISSING_BOX")
    assert "error" in result_missing
    print("   ✅ 缺失数据处理通过")


@patch("src.tools.port_tools._load_mock_data", return_value=MOCK_DB_DATA)
def test_get_customs_status(mock_load):
    """测试报关状态查询工具"""
    print("\n🧪 测试: get_customs_status")

    # 场景 1: 正常查询
    result = get_customs_status.invoke("TEST_BL_001")
    assert result["customs_status"] == "放行"
    print("   ✅ 正常数据查询通过")

    # 场景 2: 异常查询
    result_missing = get_customs_status.invoke("INVALID_BL")
    assert "error" in result_missing
    print("   ✅ 缺失数据处理通过")


@patch("src.tools.port_tools._load_mock_data", return_value=MOCK_DB_DATA)
def test_get_vessel_schedule(mock_load):
    """测试船期查询工具"""
    print("\n🧪 测试: get_vessel_schedule")

    # 场景 1: 正常查询
    result = get_vessel_schedule.invoke("测试轮")
    assert result["voyage"] == "V001"
    print("   ✅ 正常数据查询通过")

    # 场景 2: 异常查询
    result_missing = get_vessel_schedule.invoke("幽灵船")
    assert "error" in result_missing
    print("   ✅ 缺失数据处理通过")


def test_tool_metadata():
    """测试工具的元数据（名称、描述）是否符合 LangChain 要求"""
    print("\n🧪 测试: 工具元数据定义")

    tools_map = {t.name: t for t in all_tools}

    # 检查工具是否存在
    assert "get_container_status" in tools_map
    assert "get_customs_status" in tools_map
    assert "get_vessel_schedule" in tools_map

    # 检查描述是否非空 (LLM 依赖描述来决定是否调用)
    for tool in all_tools:
        assert tool.description is not None
        assert len(tool.description) > 10
        print(f"   ✅ 工具 {tool.name} 描述检查通过")


if __name__ == "__main__":
    """ 
    uv run python -m tests.tools.test_port_tools
    """
    # 允许直接运行此脚本
    # 也可以使用 pytest 运行
    try:
        test_get_container_status()
        test_get_customs_status()
        test_get_vessel_schedule()
        test_tool_metadata()
        print("\n🎉 所有 Port Tools 测试通过！")
    except AssertionError as e:
        print(f"\n❌ 测试失败: {e}")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
