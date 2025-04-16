from openai import OpenAI
from typing import Generator, Union
import os

chat_model = "THUDM/GLM-4-32B-0414"

def get_client():
    silicon_api_key = os.getenv("SILICON_API_KEY")
    return OpenAI(
        api_key=silicon_api_key,
        base_url="https://api.siliconflow.cn/v1",
    )

def get_chat_completion(
    user_prompt: str,
    user_context: str,
    max_tokens: int = 2000,
) -> Union[str, Generator[str, None, None]]:
    """
    获取聊天补全结果，支持流式和非流式输出

    参数:
        user_prompt: 用户提示
        user_context: 用户上下文
        use_stream: 是否使用流式输出
        max_tokens: 最大token数

    返回:
        如果 use_stream=True: 返回一个生成器，逐块产生响应
        如果 use_stream=False: 返回完整的响应字符串
    """
    client = get_client()
    try:
            # 非流式输出版本
        response = client.chat.completions.create(
                model=chat_model,
                messages=[{"role":"system","content":user_prompt},{"role": "user", "content": user_context}],
                temperature=0.0,
                max_tokens=max_tokens,
            )
        return response.choices[0].message.content,response.usage.completion_tokens

    except Exception as e:
        print(f"Error: {e}")
        return None 

if __name__ == "__main__":
    # 测试代码
    user_prompt = "请给我一个关于机器学习的简要介绍。"
    user_context = "我想了解机器学习的基本概念和应用。"
    result = get_chat_completion(user_prompt, user_context)
    print(result)
    # 测试嵌入