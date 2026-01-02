# src/tools/port_tools.py
import json
import os
from langchain_core.tools import tool
from typing import Dict, Any, Union

from src.config import settings


def _load_mock_data() -> Dict[str, Any]:
    """加载模拟的API数据，增加错误处理"""
    try:
        path = settings.MOCK_API_DATA_PATH
        # 兼容性处理：如果配置路径不存在，尝试在根目录找
        if not os.path.exists(path):
            if os.path.exists("mock_api_data.json"):
                path = "mock_api_data.json"
            else:
                # 返回一个特殊的标记，表明是系统级错误
                return {"_system_error": f"严重错误：数据文件未找到 ({path})"}

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        return {"_system_error": f"严重错误：读取数据失败 ({e})"}


@tool
def get_container_status(container_id: str) -> Union[dict, str]:
    """
    根据集装箱号查询集装箱的在港状态。
    包括是否进港、VGM(货物总重)状态和所在位置。
    """
    data = _load_mock_data()
    if "_system_error" in data:
        return data["_system_error"]

    # 1. 数据清洗：去除空格，转大写，防止用户手误
    clean_id = container_id.strip().upper()

    containers = data.get("containers", {})

    # 2. 查询
    result = containers.get(clean_id)

    # 3. 用户友好的未找到提示
    if not result:
        return f"系统反馈：在港区系统中未找到箱号 '{clean_id}'。请提示用户核对箱号格式（通常是4位字母+7位数字）。"

    return result


@tool
def get_customs_status(bill_of_lading: str) -> Union[dict, str]:
    """
    根据提单号查询货物的报关状态。
    例如是否放行、是否被查验以及查验代码。
    """
    data = _load_mock_data()
    if "_system_error" in data:
        return data["_system_error"]

    # 数据清洗
    clean_bill = bill_of_lading.strip().upper()

    customs = data.get("customs", {})
    result = customs.get(clean_bill)

    if not result:
        return f"系统反馈：海关系统中未查询到提单号 '{clean_bill}' 的数据。请询问用户提单号是否正确。"

    return result


@tool
def get_vessel_schedule(vessel_name: str) -> Union[dict, str]:
    """
    根据船名查询船舶的预计靠泊时间和截关时间(CVT)。
    支持模糊查询（例如输入“金牛座”可查到“中远海运金牛座”）。
    """
    data = _load_mock_data()
    if "_system_error" in data:
        return data["_system_error"]

    clean_name = vessel_name.strip()
    vessels = data.get("vessels", {})

    # 1. 优先尝试精确匹配
    if clean_name in vessels:
        return vessels[clean_name]

    # 2. 尝试模糊匹配 (Demo演示的核心亮点)
    # 遍历所有船名，看是否包含用户输入的关键词
    matched_vessels = []
    for v_key, v_data in vessels.items():
        if clean_name in v_key:
            matched_vessels.append(v_data)

    if len(matched_vessels) == 1:
        # 只有一个匹配项，直接返回
        return matched_vessels[0]
    elif len(matched_vessels) > 1:
        # 匹配到多个，返回列表让LLM让用户确认
        names = [v["vessel_name"] for v in matched_vessels]
        return (
            f"系统反馈：找到多条匹配船名: {', '.join(names)}。请询问用户具体指哪一艘。"
        )

    # 3. 确实没找到
    return f"系统反馈：在船期表中未找到包含 '{clean_name}' 的船舶。请提示用户确认船名拼写。"


# 将所有工具集中导出
all_tools = [get_container_status, get_customs_status, get_vessel_schedule]
