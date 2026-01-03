# src/web/app.py
"""
uv run streamlit run src/web/app.py
"""

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
from src.web.admin import render_admin_panel
from src.web.callbacks import AgentMonitorCallback  # 导入回调
from src.web.monitor import render_monitor_page
from langchain_community.callbacks import StreamlitCallbackHandler


INIT_MESSAGE = """ 
你好！我是**小宁**。请告诉我您的箱号、提单号或业务问题。\n
例如：\n
帮我查一下箱号 TRLU1234567 和提单号 BILL001。这票货是配‘中远海运金牛座’的，状态正常吗？\n
重点关注一下 BILL_URGENT 这票货，船名是‘东方海外宁波’。海关状态刚变成 H98，还能赶上吗？\n
最急的是提单号 BILL_RISK，也是配‘东方海外宁波’。但这票货早上9点被**‘人工查验’**了。请帮我分析一下风险，我该怎么办？\n
最后查一下箱号 NOVGM999，提单号 BILL_NOVGM。海关已经放行了，应该没问题了吧？\n
"""

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


# --- 3. 辅助函数：渲染监控面板 ---
def render_monitor_metrics(metrics: dict):
    """渲染监控数据 (Token, 耗时, RAG来源)"""
    with st.expander("📊 诊断监控面板 (Trace & Metrics)", expanded=False):
        # 1. 基础指标
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("⏱️ 耗时", f"{metrics['latency']}s")
        c2.metric("📥 Input Tokens", metrics["tokens"]["input"])
        c3.metric("📤 Output Tokens", metrics["tokens"]["output"])
        c4.metric("∑ Total Tokens", metrics["tokens"]["total"])

        # 2. RAG 召回内容
        st.markdown("#### 📖 RAG 知识库召回")
        if metrics["rag_docs"]:
            for i, doc in enumerate(metrics["rag_docs"]):
                st.info(f"**Source {i+1}**: {doc.page_content}")
        else:
            st.caption("本次回答未使用 RAG 检索或未命中知识库。")

        # 3. 工具调用日志 (可选)
        if metrics.get("tool_calls"):
            st.markdown("#### 🛠️ 工具调用链")
            st.json(metrics["tool_calls"])


# --- 4. 聊天视图逻辑 ---
def render_chat_view(agent_executor):
    st.title("🚢 智能口岸异常诊断助手")

    # 初始化消息结构: {"role": str, "content": str, "metrics": dict/None}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {
                "role": "assistant",
                "content": INIT_MESSAGE,
                "metrics": None,
            }
        ]

    # 渲染历史
    for msg in st.session_state.chat_history:
        avatar = "🤖" if msg["role"] == "assistant" else "👤"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])
            # 如果存在监控数据，且是 AI 回复，则显示面板
            if msg.get("metrics"):
                render_monitor_metrics(msg["metrics"])

    # 处理输入
    if prompt := st.chat_input("请输入查询内容..."):
        # 1. 显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.markdown(prompt)
        st.session_state.chat_history.append(
            {"role": "user", "content": prompt, "metrics": None}
        )

        # 2. 处理 AI 响应
        if agent_executor:
            with st.chat_message("assistant", avatar="🤖"):
                msg_placeholder = st.empty()

                # --- 修改开始 ---

                # 创建状态容器
                with st.status("🔍 小宁正在分析...", expanded=True) as status_container:

                    # 2. 初始化 Streamlit 专用回调，指定父容器为 status_container
                    # 这样中间步骤就会打印在“分析完成”这个折叠框里
                    st_callback = StreamlitCallbackHandler(
                        parent_container=status_container
                    )

                    # 初始化原本的监控回调 (用于后台记录数据)
                    monitor_callback = AgentMonitorCallback()

                    try:
                        # 3. 执行 Agent，同时传入两个回调：
                        # st_callback 用于前端展示思考过程
                        # monitor_callback 用于后台统计 Token 和日志
                        response = agent_executor.invoke(
                            {"input": prompt},
                            config={"callbacks": [monitor_callback, st_callback]},
                        )

                        result_text = response["output"]

                        # 更新状态栏为完成
                        status_container.update(
                            label="✅ 分析完成 (点击查看思考过程)",
                            state="complete",
                            expanded=False,
                        )

                    except Exception as e:
                        status_container.update(label="❌ 发生错误", state="error")
                        st.error(f"系统错误: {e}")
                        return  # 遇到错误提前结束

                # --- 修改结束 ---

                # 打字机输出最终结果
                msg_placeholder.write_stream(typewriter_effect(result_text))

                # 整理监控数据
                metrics_data = {
                    "latency": monitor_callback.latency,
                    "tokens": monitor_callback.token_usage,
                    "rag_docs": monitor_callback.rag_documents,
                    "tool_calls": monitor_callback.tool_calls,
                }

                # 显示本次监控面板
                render_monitor_metrics(metrics_data)

                # 保存到历史
                st.session_state.chat_history.append(
                    {
                        "role": "assistant",
                        "content": result_text,
                        "metrics": metrics_data,
                    }
                )
            # except Exception as e:
            #     status_container.update(label="❌ 发生错误", state="error")
            #     st.error(f"系统错误: {e}")


# --- 5. 主入口 ---
def main():
    load_css()
    current_page = render_sidebar()

    if current_page == "💬 智能对话":
        agent = get_agent_engine()
        render_chat_view(agent)

    elif current_page == "🛠️ 数据配置":
        render_admin_panel()

    elif current_page == "🔍 历史审计":
        render_monitor_page()


if __name__ == "__main__":
    main()
