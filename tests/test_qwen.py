import os
from pathlib import Path
from dotenv import load_dotenv
import dashscope
from http import HTTPStatus

def test_qwen_api_call():
    # 1. 加载 .env 文件中的环境变量
    # 假设你的 .env 文件在父级目录
    env_path = Path(__file__).resolve().parent.parent / '.env'
    print(f"正在尝试加载 .env 文件: {env_path}") 

    loaded = load_dotenv(dotenv_path=env_path)
    if not loaded:
        print("警告：load_dotenv 返回 False，可能未找到文件或文件为空。")
    
    # 2. 从环境变量获取 API Key
    # 阿里云 DashScope 的 Key 通常命名为 DASHSCOPE_API_KEY
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if not api_key:
        print("错误：未在 .env 文件中找到 DASHSCOPE_API_KEY，请检查变量名是否一致。")
    else:
        print("成功读取 API Key，开始调用接口...")
        
        # 3. 设置 API Key (DashScope 可以通过全局变量设置)
        dashscope.api_key = api_key

        try:
            # 4. 发起请求
            # qwen-turbo 是基础模型，速度快且便宜/免费额度多
            response = dashscope.Generation.call(
                model="qwen-turbo", 
                messages=[
                    {'role': 'system', 'content': '你是一个有用的助手。'},
                    {'role': 'user', 'content': '你好，测试一下Qwen API调用是否成功。'}
                ],
                # result_format='message' 建议加上，使得返回结构更像 OpenAI 格式
                result_format='message'  
            )
            
            # 5. 输出结果
            # DashScope 的返回结构与 ZhipuAI 略有不同，需要检查 status_code
            if response.status_code == HTTPStatus.OK:
                print("-" * 30)
                print("回复内容：")
                # 获取回复内容
                print(response.output.choices[0]['message']['content'])
                print("-" * 30)
            else:
                print(f"请求失败，状态码: {response.status_code}")
                print(f"错误代码: {response.code}")
                print(f"错误信息: {response.message}")

        except Exception as e:
            print(f"接口调用发生异常: {e}")

if __name__ == "__main__":
    test_qwen_api_call()
    print('Done')