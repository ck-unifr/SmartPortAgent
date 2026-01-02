# src/web/sidebar.py
import streamlit as st
from src.config import settings


def render_sidebar():
    """渲染侧边栏，并返回当前选择的页面模式"""
    with st.sidebar:
        st.title("🚢 智能口岸助手")

        # --- 模式导航 ---
        st.markdown("### 🧭 模式选择")
        page_mode = st.radio(
            "选择功能模块:",
            # ["💬 智能对话", "🛠️ 数据配置"],
            ["💬 智能对话", "🛠️ 数据配置", "🔍 历史审计"],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # --- 对话模式下的快捷操作 ---
        if page_mode == "💬 智能对话":
            st.markdown("### ⚡ 快捷操作")
            if st.button("🗑️ 清空对话历史", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

            st.markdown("---")
            st.markdown("### 📚 系统状态")
            st.caption(f"LLM 引擎: `{settings.LLM_PROVIDER.upper()}`")
            st.success("✅ 知识库服务就绪")
            pass

        # --- 版本信息 ---
        st.markdown("---")
        st.caption(f"Smart Port Agent v0.2.0\n© 2026 国际物流网")

    return page_mode
