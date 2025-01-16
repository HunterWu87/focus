"""翻译服务模块"""
import requests
from typing import List
from . import config

class TranslationService:
    def __init__(self, api_key: str = config.DEEPSEEK_API_KEY):
        """初始化翻译服务"""
        self.api_key = api_key
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

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
        
        # 构造API请求数据
        data = {
            "model": "deepseek-chat",  # 自动使用最新的V3版本
            "messages": [
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
            "temperature": 0.3,  # 降低随机性，保持翻译准确
            "stream": False      # 非流式输出
        }
        
        try:
            # 发送API请求
            response = requests.post(
                config.DEEPSEEK_API_URL,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            
            # 解析返回的翻译结果
            response_text = result['choices'][0]['message']['content'].strip()
            
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
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")
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
        data = {
            "model": "deepseek-chat",
            "messages": [
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
            "temperature": 0.3,
            "stream": False
        }
        
        try:
            response = requests.post(
                config.DEEPSEEK_API_URL,
                headers=self.headers,
                json=data
            )
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {str(e)}")
        except Exception as e:
            raise Exception(f"总结处理失败: {str(e)}") 