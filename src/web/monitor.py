import streamlit as st
import pandas as pd
from src.database.repository import ChatLogRepository


def render_monitor_page():
    st.title("🛡️ 审计监控中心 (Audit Dashboard)")
    st.caption("实时监控 Agent 的对话历史、Token 消耗及工具调用链路。")

    # 1. 数据获取
    logs = ChatLogRepository.get_recent_logs(limit=100)

    if not logs:
        st.info("📭 暂无审计日志数据。")
        return

    # 2. 转换数据为 DataFrame 用于统计
    data = []
    for log in logs:
        data.append(
            {
                "ID": log.id,
                "时间": log.timestamp,
                "用户提问": log.user_input,
                "耗时(s)": log.latency,
                "Total Tokens": log.total_tokens,
                "状态": "✅" if log.status == "success" else "❌",
            }
        )
    df = pd.DataFrame(data)

    # 3. 顶部关键指标 (KPIs)
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("总调用次数", len(df))
    with col2:
        avg_latency = df["耗时(s)"].mean()
        st.metric("平均响应耗时", f"{avg_latency:.2f} s")
    with col3:
        total_cost = df["Total Tokens"].sum()
        st.metric("总 Token 消耗", f"{total_cost:,}")
    with col4:
        error_rate = len(df[df["状态"] == "❌"]) / len(df) * 100 if len(df) > 0 else 0
        st.metric("错误率", f"{error_rate:.1f}%")

    st.markdown("---")

    # 4. 详细日志表格视图
    st.subheader("📜 调用流水日志")

    # 使用 dataframe 并允许选择行（Streamlit 1.30+ 功能，如果版本低可用普通 dataframe）
    st.dataframe(
        df,
        column_config={
            "时间": st.column_config.DatetimeColumn("请求时间", format="MM-DD HH:mm"),
            "用户提问": st.column_config.TextColumn("用户提问", width="medium"),
        },
        use_container_width=True,
        hide_index=True,
    )

    # 5. 详情透视 (Drill Down)
    st.subheader("🔍 深度诊断")
    selected_id = st.selectbox(
        "选择日志 ID 查看详情:",
        options=df["ID"].tolist(),
        format_func=lambda x: f"Log #{x}",
    )

    if selected_id:
        target_log = next((l for l in logs if l.id == selected_id), None)
        if target_log:
            with st.container(border=True):
                c1, c2 = st.columns([1, 1])
                with c1:
                    st.markdown("#### 🗣️ User Input")
                    st.info(target_log.user_input)
                with c2:
                    st.markdown("#### 🤖 AI Output")
                    if target_log.status == "success":
                        st.success(target_log.ai_output)
                    else:
                        st.error(f"Error: {target_log.error_message}")

                # 中间步骤可视化
                st.markdown("#### 🛠️ Execution Trace (工具链)")
                if target_log.intermediate_steps:
                    for step in target_log.intermediate_steps:
                        with st.expander(
                            f"🔧 Tool: {step.get('tool')} ({step.get('timestamp')})"
                        ):
                            st.code(step.get("result"), language="json")
                else:
                    st.caption("无工具调用记录")

                # RAG 召回
                st.markdown("#### 📖 RAG Context")
                if target_log.rag_sources:
                    for idx, src in enumerate(target_log.rag_sources):
                        st.text(f"[{idx+1}] {src}...")
                else:
                    st.caption("未触发 RAG 检索")

                # 技术元数据
                st.divider()
                st.json(
                    {
                        "latency": target_log.latency,
                        "tokens": {
                            "input": target_log.input_tokens,
                            "output": target_log.output_tokens,
                            "total": target_log.total_tokens,
                        },
                        "timestamp": str(target_log.timestamp),
                    }
                )
