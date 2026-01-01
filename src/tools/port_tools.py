# src/tools/port_tools.py
import json
import os
from langchain_core.tools import tool
from typing import Dict, Any

from src.config import settings


def _load_mock_data() -> Dict[str, Any]:
    """加载模拟的API数据，增加错误处理"""
    try:
        path = settings.MOCK_API_DATA_PATH
        if not os.path.exists(path):
            # 尝试在当前目录查找（防止路径配置错误）
            if os.path.exists("mock_api_data.json"):
                path = "mock_api_data.json"
            else:
                return {
                    "error": f"数据文件未找到: {path}",
                    "containers": {},
                    "customs": {},
                    "vessels": {},
                }

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {
            "error": f"读取数据失败: {e}",
            "containers": {},
            "customs": {},
            "vessels": {},
        }


@tool
def get_container_status(container_id: str) -> dict:
    """
    根据集装箱号查询集装箱的在港状态。
    包括是否进港、VGM(货物总重)状态和所在位置。
    """
    data = _load_mock_data()
    # 安全获取嵌套字典
    containers = data.get("containers", {})
    return containers.get(
        container_id, {"error": f"未找到集装箱 {container_id} 的信息"}
    )


@tool
def get_customs_status(bill_of_lading: str) -> dict:
    """
    根据提单号查询货物的报关状态。
    例如是否放行、是否被查验以及查验代码。
    """
    data = _load_mock_data()
    customs = data.get("customs", {})
    return customs.get(
        bill_of_lading, {"error": f"未找到提单 {bill_of_lading} 的报关信息"}
    )


@tool
def get_vessel_schedule(vessel_name: str) -> dict:
    """
    根据船名查询船舶的预计靠泊时间和截关时间(CVT)。
    """
    data = _load_mock_data()
    vessels = data.get("vessels", {})
    return vessels.get(vessel_name, {"error": f"未找到船舶 {vessel_name} 的船期信息"})


# 将所有工具集中导出
all_tools = [get_container_status, get_customs_status, get_vessel_schedule]
