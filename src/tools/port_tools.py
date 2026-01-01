# src/tools/port_tools.py
import json
from langchain_core.tools import tool
from typing import Optional

from src.config import settings


def _load_mock_data():
    """加载模拟的API数据"""
    with open(settings.MOCK_API_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@tool
def get_container_status(container_id: str) -> dict:
    """
    根据集装箱号查询集装箱的在港状态。
    包括是否进港、VGM(货物总重)状态和所在位置。
    """
    data = _load_mock_data()
    return data["containers"].get(container_id, {"error": "未找到该集装箱信息"})


@tool
def get_customs_status(bill_of_lading: str) -> dict:
    """
    根据提单号查询货物的报关状态。
    例如是否放行、是否被查验以及查验代码。
    """
    data = _load_mock_data()
    return data["customs"].get(bill_of_lading, {"error": "未找到该提单的报关信息"})


@tool
def get_vessel_schedule(vessel_name: str) -> dict:
    """
    根据船名查询船舶的预计靠泊时间和截关时间(CVT)。
    """
    data = _load_mock_data()
    return data["vessels"].get(vessel_name, {"error": "未找到该船舶的船期信息"})


# 将所有工具集中导出
all_tools = [get_container_status, get_customs_status, get_vessel_schedule]
