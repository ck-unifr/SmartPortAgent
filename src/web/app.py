import sys
import os
from pathlib import Path

# 将项目根目录加入路径，确保能导入 src 模块
current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent
sys.path.append(str(root_dir))

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from src.agent.agent_creator import create_port_agent
from src.web.utils import load_css, typewriter_effect
from src.web.sidebar import render_sidebar

# --- 1. 页面配置 ---
st.set_page_config(
    page_title="小宁 - 智能口岸助手",
    page_icon="🚢",
    layout="centered",  # 使用居中布局模仿 ChatGPT
)


# --- 2. 初始化资源 (带缓存) ---
@st.cache_resource
def get_agent_engine():
    """初始化 Agent，利用缓存避免重复加载向量库"""
    try:
        return create_port_agent()
    except Exception as e:
        st.error(f"Agent 初始化失败: {e}")
        return None


# --- 3. 状态管理 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(
            content="你好！我是**小宁**，国际物流网的业务专家。\n\n我可以帮你查询：\n- 📦 **集装箱状态** (如：箱号 NBCT...)\n- 📄 **报关进度** (如：提单号 BILL...)\n- 🚢 **船期与截关时间**\n\n请告诉我您的需求。"
        )
    ]


# --- 4. 核心渲染逻辑 ---
def main():
    load_css()
    render_sidebar()

    st.title("🚢 智能口岸异常诊断助手")

    agent_executor = get_agent_engine()

    # 4.1 渲染历史消息
    for msg in st.session_state.messages:
        if isinstance(msg, AIMessage):
            with st.chat_message("assistant", avatar="🤖"):
                st.markdown(msg.content)
        elif isinstance(msg, HumanMessage):
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg.content)

    # 4.2 处理用户输入
    if prompt := st.chat_input("请输入箱号、提单号或业务问题..."):
        # 显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.messages.append(HumanMessage(content=prompt))

        # 处理 AI 响应
        if agent_executor:
            with st.chat_message("assistant", avatar="🤖"):
                message_placeholder = st.empty()
                full_response = ""

                try:
                    # 显示加载状态
                    with st.spinner("🔍 小宁正在查询数据并检索法规..."):
                        # 调用 Agent
                        response_payload = agent_executor.invoke({"input": prompt})
                        result_text = response_payload["output"]

                    # 打字机效果渲染
                    message_placeholder.write_stream(typewriter_effect(result_text))

                    # 更新历史
                    st.session_state.messages.append(AIMessage(content=result_text))

                except Exception as e:
                    st.error(f"发生错误: {str(e)}")
        else:
            st.error("Agent 服务未就绪，请检查后台配置。")


if __name__ == "__main__":
    """
    uv run streamlit run src/web/app.py

    query:
    帮我查一下箱号 NBCT1234567，提单号 BILL002。这票货明天能赶上“中远海运金牛座”吗？我很急，一直没放行。
    
    查一下集装箱 TRLU1234567，提单号 BILL001。船名是“中远海运金牛座”。一切正常吗？
    
    帮我查个不存在的箱子 ERROR999999，看看什么情况。
    """
    main()
