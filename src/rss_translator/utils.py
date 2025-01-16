"""工具函数模块"""
from typing import Dict, Any

def print_feed_info(title: str, description: str) -> None:
    """打印RSS源信息"""
    print('\n=== RSS源信息 ===')
    print(f'标题: {title}')
    print(f'描述: {description if description else "无描述"}')

def print_article_entry(index: int, translated_title: str, original_title: str) -> None:
    """打印文章条目"""
    print(f'[{index}] {translated_title}')
    print(f'     原标题: {original_title}')
    print('-' * 50) 