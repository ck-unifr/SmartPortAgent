import os
from pathlib import Path
from dotenv import load_dotenv
from zhipuai import ZhipuAI


def test_chatglm_api_call():
    # 1. 加载 .env 文件中的环境变量
    env_path = Path(__file__).resolve().parent.parent / '.env'
    print(f"正在尝试加载 .env 文件: {env_path}") # 打印路径方便调试

    loaded = load_dotenv(dotenv_path=env_path)
    if not loaded:
        print("警告：load_dotenv 返回 False，可能未找到文件或文件为空。")
    
    # 2. 从环境变量获取 API Key
    # 请将 "ZHIPU_API_KEY" 替换为你 .env 文件里实际定义的变量名
    api_key = os.getenv("ZHIPU_API_KEY")

    # 简单的检查，防止 Key 读取失败导致后续报错
    if not api_key:
        print("错误：未在 .env 文件中找到 API Key，请检查变量名是否一致。")
    else:
        print("成功读取 API Key，开始调用接口...")
        
        # 3. 初始化客户端
        client = ZhipuAI(api_key=api_key)

        try:
            # 4. 发起请求
            response = client.chat.completions.create(
                model="glm-4",  # 可以换成 glm-4-flash (免费/快速)
                messages=[
                    {"role": "user", "content": "你好，测试一下API调用是否成功。"},
                ],
            )
            
            # 5. 输出结果
            print("-" * 30)
            print("回复内容：")
            print(response.choices[0].message.content)
            print("-" * 30)

        except Exception as e:
            print(f"接口调用失败: {e}")


if __name__ == "__main__":
    """ 
    uv run ./tests/test_chatglm.py
    """
    test_chatglm_api_call()
    print('Done')