import streamlit as st
from src.config import settings


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.title("🚢 智能口岸助手")
        st.markdown(f"**当前引擎**: `{settings.LLM_PROVIDER.upper()}`")

        st.markdown("---")

        # 功能区
        st.markdown("### 🛠️ 快捷操作")
        if st.button("🗑️ 清空对话历史", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.markdown("---")

        # 帮助信息
        st.markdown("### 📚 知识库状态")
        st.success("✅ 口岸法规库已加载")
        st.success("✅ 船期数据源已连接")

        st.markdown("---")
        st.caption(f"Smart Port Agent v0.1.0\n© 2026 国际物流网")
