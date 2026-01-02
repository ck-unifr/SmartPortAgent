# src/web/utils.py

import streamlit as st
import time


def load_css():
    """注入自定义CSS，隐藏默认元素，优化对话气泡样式"""
    st.markdown(
        """
        <style>
        /* --- 1. 顶部 Header 处理 (修复侧边栏无法复原的关键) --- */
        
        /* ❌ 绝对不要使用 header {visibility: hidden;}，这会把侧边栏按钮也藏起来 */
        
        /* ✅ 正确做法：隐藏右上角汉堡菜单 */
        #MainMenu {visibility: hidden;}
        
        /* ✅ 正确做法：隐藏页脚 "Made with Streamlit" */
        footer {visibility: hidden;}
        
        /* ✅ 正确做法：将 Header 背景设为透明，这样看起来像没有 Header，但按钮还在 */
        [data-testid="stHeader"] {
            background-color: rgba(0,0,0,0); /* 透明背景 */
        }
        
        /* (可选) 隐藏顶部的彩色装饰线条 */
        [data-testid="stDecoration"] {
            display: none;
        }

        /* --- 2. 布局优化 --- */
        
        /* 调整主容器宽度，使其更像聊天窗口 */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            max-width: 800px;
        }
        
        /* 优化聊天输入框 */
        .stChatInput {
            border-color: #e5e5e5;
        }
        
        /* --- 3. 自定义样式 --- */
        
        /* 自定义提示信息样式 */
        .info-box {
            background-color: #f7f7f8;
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 20px;
            font-size: 0.9em;
            color: #666;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )


def typewriter_effect(text: str):
    """模拟流式打字机效果输出文本"""
    # 增加空值检查，防止 text 为 None 时报错
    if not text:
        return

    for word in text.split():
        yield word + " "
        time.sleep(0.02)
