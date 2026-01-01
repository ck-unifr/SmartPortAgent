import streamlit as st
import time


def load_css():
    """注入自定义CSS，隐藏默认元素，优化对话气泡样式"""
    st.markdown(
        """
        <style>
        /* 隐藏 Streamlit 默认的汉堡菜单和页脚 */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* 调整主容器宽度，使其更像聊天窗口 */
        .block-container {
            padding-top: 2rem;
            padding-bottom: 5rem;
            max_width: 800px;
        }
        
        /* 优化聊天输入框 */
        .stChatInput {
            border-color: #e5e5e5;
        }
        
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
    for word in text.split():
        yield word + " "
        time.sleep(0.02)
