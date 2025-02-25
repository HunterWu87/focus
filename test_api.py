"""测试腾讯云 DeepSeek API 连接"""
import os
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

def test_api():
    # 加载环境变量
    load_dotenv(find_dotenv())
    
    # 获取API密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    print("\n=== API配置信息 ===")
    print(f"API密钥: {api_key[:6]}..." if api_key else "未找到API密钥")
    
    if not api_key:
        print("错误: 请在.env文件中设置DEEPSEEK_API_KEY")
        return
    
    # 初始化客户端
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.lkeap.cloud.tencent.com/v1"
    )
    
    try:
        print("\n=== 测试API连接 ===")
        print("发送测试请求...")
        
        # 发送测试请求
        completion = client.chat.completions.create(
            model="deepseek-v3",
            messages=[
                {
                    "role": "user",
                    "content": "Hello, this is a test message."
                }
            ],
            temperature=0.7,
            top_p=0.6,
            presence_penalty=0.95
        )
        
        print("\n=== 响应结果 ===")
        print("状态: 成功")
        print(f"模型: {completion.model}")
        print(f"响应: {completion.choices[0].message.content}")
        print("\n=== 测试完成 ===")
        
    except Exception as e:
        print("\n=== 错误信息 ===")
        print(f"状态: 失败")
        print(f"错误: {str(e)}")
        print("\n=== 测试失败 ===")

if __name__ == "__main__":
    test_api()

