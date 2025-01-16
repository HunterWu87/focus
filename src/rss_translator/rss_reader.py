"""RSS阅读器模块"""
import time
import webbrowser
import feedparser
import requests
from typing import List, Tuple, Optional
from bs4 import BeautifulSoup
from . import config
from . import utils
from .translator import TranslationService

class RSSReader:
    def __init__(self, translator: TranslationService):
        self.translator = translator
        self.articles: List[Tuple[str, str, str]] = []  # [(标题, 翻译, URL)]

    def fetch_feed(self, url: str = config.DEFAULT_RSS_URL) -> None:
        """获取并解析RSS源"""
        # 显示版本信息
        print(f"\n=== RSS翻译器 v{config.APP_VERSION} ===")
        print(f"翻译模型: {config.MODEL_NAME} ({config.MODEL_VERSION})")
        print("=" * 40)
        
        feed = feedparser.parse(url)
        utils.print_feed_info(feed.feed.title, feed.feed.get('description', ''))
        
        print('\n=== 文章列表 ===')
        self.articles.clear()
        
        # 收集所有标题
        titles = [entry.title for entry in feed.entries]
        
        try:
            # 批量翻译所有标题
            translated_titles = self.translator.translate_batch(titles)
            
            # 保存文章信息并显示
            for index, (entry, translated_title) in enumerate(zip(feed.entries, translated_titles), 1):
                utils.print_article_entry(index, translated_title, entry.title)
                self.articles.append((entry.title, translated_title, entry.link))
                
        except Exception as e:
            print(f"翻译过程出错: {str(e)}")
            # 如果翻译失败，仍然保存文章信息，但不包含翻译
            for index, entry in enumerate(feed.entries, 1):
                utils.print_article_entry(index, f"(翻译失败)", entry.title)
                self.articles.append((entry.title, "", entry.link))

    def get_article_content(self, url: str) -> Optional[str]:
        """
        获取文章内容
        
        Args:
            url: 文章URL
            
        Returns:
            Optional[str]: 文章内容，如果获取失败则返回None
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 移除脚本和样式元素
            for script in soup(['script', 'style']):
                script.decompose()
            
            # 获取正文内容
            text = soup.get_text()
            
            # 清理文本
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text
        except Exception:
            return None

    def interactive_mode(self) -> None:
        """交互式模式"""
        while True:
            try:
                choice = input('\n请输入文章编号来打开网页，输入"s数字"查看文章总结 (例如: s1)，输入q退出: ')
                
                if choice.lower() == 'q':
                    break
                
                if choice.lower().startswith('s'):
                    # 处理总结请求
                    try:
                        article_num = int(choice[1:])
                        if 1 <= article_num <= len(self.articles):
                            print(f'\n正在获取并总结文章 {article_num}...')
                            article = self.articles[article_num - 1]
                            content = self.get_article_content(article[2])
                            
                            if content:
                                summary = self.translator.summarize_article(article[0], content)
                                print("\n=== 文章总结 ===")
                                print(f"标题: {article[1]}")  # 显示中文标题
                                print(f"原标题: {article[0]}")
                                print("\n摘要:")
                                print(summary)
                            else:
                                print("无法获取文章内容，请直接访问原文。")
                        else:
                            print(f'请输入1到{len(self.articles)}之间的数字')
                    except ValueError:
                        print('无效的文章编号')
                    continue
                
                # 处理打开网页请求
                article_num = int(choice)
                if 1 <= article_num <= len(self.articles):
                    print(f'正在打开文章: {article_num}')
                    webbrowser.open(self.articles[article_num - 1][2])
                else:
                    print(f'请输入1到{len(self.articles)}之间的数字')
            except ValueError:
                print('请输入有效的数字或q退出')