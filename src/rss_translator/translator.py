"""翻译服务模块"""
from typing import List
from openai import OpenAI
from . import config

class TranslationService:
    def __init__(self, api_key: str = config.DEEPSEEK_API_KEY):
        """初始化翻译服务"""
        self.client = OpenAI(
            api_key=api_key,
            base_url=config.DEEPSEEK_BASE_URL
        )

    def translate_batch(self, texts: List[str]) -> List[str]:
        """
        批量翻译文本（使用DeepSeek-V3）
        
        Args:
            texts: 要翻译的文本列表
            
        Returns:
            List[str]: 翻译后的文本列表
        """
        # 将所有标题组合成一个文本，用编号标记
        combined_text = "\n".join(f"{i+1}. {text}" for i, text in enumerate(texts))
        
        try:
            # 使用OpenAI SDK发送请求
            completion = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional translator. Translate English news titles to Chinese. Keep translations concise and accurate."
                    },
                    {
                        "role": "user",
                        "content": f"""Please translate these English titles to Chinese. Keep the numbering format and only return the translations:

{combined_text}"""
                    }
                ],
                temperature=config.DEFAULT_TEMPERATURE,
                top_p=config.DEFAULT_TOP_P,
                presence_penalty=config.PRESENCE_PENALTY,
                max_tokens=1024
            )
            
            # 解析返回的翻译结果
            response_text = completion.choices[0].message.content.strip()
            
            # 处理翻译结果，提取每个标题的翻译
            translations = []
            for line in response_text.split('\n'):
                line = line.strip()
                if line:
                    # 移除编号和点号，只保留翻译内容
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        translations.append(parts[1].strip())
            
            # 验证翻译结果数量
            if len(translations) != len(texts):
                raise Exception(f"翻译结果数量不匹配: 期望 {len(texts)}, 实际 {len(translations)}")
            
            return translations
            
        except Exception as e:
            raise Exception(f"翻译处理失败: {str(e)}")

    def summarize_article(self, title: str, content: str) -> str:
        """
        使用DeepSeek-V3对文章内容进行总结
        
        Args:
            title: 文章标题
            content: 文章内容
            
        Returns:
            str: 300-500字的中文总结
        """
        # 限制输入长度
        if len(content) > config.MAX_INPUT_LENGTH:
            content = content[:config.MAX_INPUT_LENGTH]
            
        try:
            completion = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的新闻文章总结专家。请用中文总结文章要点，确保总结在300-500字之间，突出文章的关键信息、背景和影响。"
                    },
                    {
                        "role": "user",
                        "content": f"""请总结以下文章：

标题：{title}

内容：{content}

要求：
1. 总结字数在300-500字之间
2. 包含主要事件、关键人物和重要数据
3. 分析事件影响和意义
4. 使用客观准确的语言"""
                    }
                ],
                temperature=config.DEFAULT_TEMPERATURE,
                top_p=config.DEFAULT_TOP_P,
                presence_penalty=config.PRESENCE_PENALTY,
                max_tokens=1024
            )
            
            return completion.choices[0].message.content.strip()
            
        except Exception as e:
            raise Exception(f"总结处理失败: {str(e)}") 