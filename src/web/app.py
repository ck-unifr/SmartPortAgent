# src/web/app.py
import sys
import streamlit as st
from pathlib import Path

# 路径配置
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent
sys.path.append(str(root_dir))

from langchain_core.messages import AIMessage, HumanMessage
from src.agent.agent_creator import create_port_agent
from src.web.utils import load_css, typewriter_effect
from src.web.sidebar import render_sidebar
from src.web.admin import render_admin_panel  # 导入新模块

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="小宁 - 智能口岸助手",
    page_icon="🚢",
    layout="centered",
)


# --- 2. 资源初始化 ---
@st.cache_resource
def get_agent_engine():
    try:
        return create_port_agent()
    except Exception as e:
        st.error(f"Agent 初始化失败: {e}")
        return None


# --- 3. 聊天视图逻辑 ---
def render_chat_view(agent_executor):
    st.title("🚢 智能口岸异常诊断助手")

    # 初始化消息
    if "messages" not in st.session_state:
        st.session_state.messages = [
            AIMessage(
                content="你好！我是**小宁**。请告诉我您的箱号、提单号或业务问题。"
            )
        ]

    # 渲染历史
    for msg in st.session_state.messages:
        avatar = "🤖" if isinstance(msg, AIMessage) else "👤"
        with st.chat_message(
            "assistant" if isinstance(msg, AIMessage) else "user", avatar=avatar
        ):
            st.markdown(msg.content)

    # 处理输入
    if prompt := st.chat_input("请输入查询内容..."):
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(content=prompt))

        if agent_executor:
            with st.chat_message("assistant", avatar="🤖"):
                msg_placeholder = st.empty()
                with st.spinner("🔍 正在检索数据与法规..."):
                    try:
                        response = agent_executor.invoke({"input": prompt})
                        result = response["output"]
                        msg_placeholder.write_stream(typewriter_effect(result))
                        st.session_state.messages.append(AIMessage(content=result))
                    except Exception as e:
                        st.error(f"系统错误: {e}")


# --- 4. 主入口 ---
def main():
    load_css()

    # 获取当前选中的页面模式
    current_page = render_sidebar()

    if current_page == "💬 智能对话":
        agent = get_agent_engine()
        render_chat_view(agent)

    elif current_page == "🛠️ 数据配置":
        # 如果进入配置页，验证密码（可选）或直接显示
        render_admin_panel()


if __name__ == "__main__":
    """
    uv run streamlit run src/web/app.py

    query:
    帮我查一下箱号 NBCT1234567，提单号 BILL002。这票货明天能赶上“中远海运金牛座”吗？我很急，一直没放行。

    查一下集装箱 TRLU1234567，提单号 BILL001。船名是“中远海运金牛座”。一切正常吗？

    帮我查个不存在的箱子 ERROR999999，看看什么情况。
    """
    main()
