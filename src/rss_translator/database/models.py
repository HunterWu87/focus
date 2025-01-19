"""数据库模型定义"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Article:
    """文章模型"""
    id: Optional[int]
    title: str            # 原始标题
    translated_title: str  # 翻译后的标题
    url: str              # 文章URL
    source: str           # RSS源
    created_at: datetime  # 创建时间
    summary: Optional[str] = None

    def __init__(self, id: Optional[int], title: str, translated_title: str, 
                 url: str, source: str, created_at: datetime, summary: Optional[str] = None):
        self.id = id
        self.title = title
        self.translated_title = translated_title
        self.url = url
        self.source = source
        self.created_at = created_at
        self.summary = summary 