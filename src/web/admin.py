# src/web/admin.py
import streamlit as st
import json
from pathlib import Path
from src.config import settings


def _read_file(path: Path) -> str:
    """安全读取文件内容，若不存在则返回空字符串"""
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _save_file(path: Path, content: str, is_json: bool = False) -> bool:
    """保存文件，包含基础的 JSON 格式校验"""
    try:
        if is_json:
            json.loads(content)  # 校验 JSON 格式
        path.write_text(content, encoding="utf-8")
        return True
    except json.JSONDecodeError:
        st.error("❌ JSON 格式错误，请检查语法！")
        return False
    except Exception as e:
        st.error(f"❌ 保存失败: {e}")
        return False


def render_admin_panel():
    """渲染数据管理面板"""
    st.title("🛠️ 数据源管理控制台")
    st.info("在此处修改的数据将直接影响 Agent 的回答逻辑，请谨慎操作。")

    tab1, tab2 = st.tabs(["📜 口岸法规库 (RAG)", "🚢 船期数据源 (Mock API)"])

    # --- Tab 1: 知识库管理 ---
    with tab1:
        st.subheader("口岸法规知识库")
        kb_content = _read_file(settings.KNOWLEDGE_BASE_PATH)

        new_kb_content = st.text_area(
            "编辑法规文本 (每行一条规则)", value=kb_content, height=400, key="kb_editor"
        )

        if st.button("💾 保存法规库", type="primary"):
            if _save_file(settings.KNOWLEDGE_BASE_PATH, new_kb_content):
                st.success("✅ 法规库已更新！(建议重启应用以重新建立索引)")
                # 实际生产中这里可以触发重建 Vector Store 的逻辑

    # --- Tab 2: 模拟数据管理 ---
    with tab2:
        st.subheader("模拟 API 数据 (JSON)")
        api_content = _read_file(settings.MOCK_API_DATA_PATH)

        new_api_content = st.text_area(
            "编辑 JSON 数据", value=api_content, height=400, key="api_editor"
        )

        if st.button("💾 保存数据源", type="primary"):
            if _save_file(settings.MOCK_API_DATA_PATH, new_api_content, is_json=True):
                st.success("✅ 船期数据已更新！")
