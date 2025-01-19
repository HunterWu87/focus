"""RSS阅读器模块"""
import time
import webbrowser
import feedparser
import requests
from typing import List, Tuple, Optional, Callable
from bs4 import BeautifulSoup
from . import config
from . import utils
from .translator import TranslationService
from .database.manager import DatabaseManager
from .database.models import Article
from datetime import datetime
import threading
from queue import Queue

class RSSReader:
    def __init__(self, translator: TranslationService):
        self.translator = translator
        self.articles: List[Tuple[str, str, str]] = []  # [(标题, 翻译, URL)]
        self.db = DatabaseManager()
        self.translation_queue = Queue()
        self.processed_articles = Queue()
        self.status_callback = None  # 初始化状态回调属性
        self.log_callback = None  # 添加日志回调

    def set_status_callback(self, callback: Callable[[str, bool], None]):
        """设置状态更新回调函数"""
        self.status_callback = callback

    def set_log_callback(self, callback: Callable[[str], None]):
        """设置日志回调函数"""
        self.log_callback = callback

    def translate_worker(self, titles: List[str]):
        """翻译工作线程"""
        try:
            translated_titles = self.translator.translate_batch(titles)
            self.translation_queue.put(translated_titles)
        except Exception as e:
            print(f"翻译过程出错: {str(e)}")
            self.translation_queue.put(None)

    def update_feed_worker(self, url: str):
        """后台更新线程：获取RSS、翻译标题、保存到数据库"""
        try:
            if self.log_callback:
                self.log_callback("=== 开始更新RSS ===")
            if self.status_callback:
                self.status_callback("↻ 获取RSS源...", False)
            if self.log_callback:
                self.log_callback("正在获取RSS源...")
            
            # 获取RSS
            feed = feedparser.parse(url)
            if self.log_callback:
                self.log_callback(f"RSS源标题: {feed.feed.get('title', '未知')}")
            
            if self.status_callback:
                self.status_callback("↻ 对比新文章...", False)
            if self.log_callback:
                self.log_callback("\n正在对比新文章...")
            
            # 获取所有RSS条目的URL
            feed_urls = [entry.link for entry in feed.entries]
            if self.log_callback:
                self.log_callback(f"RSS源文章总数: {len(feed_urls)}篇")
            
            # 从数据库获取已存在的URL
            existing_articles = self.db.get_articles_by_source(url)
            existing_urls = {article.url for article in existing_articles}
            if self.log_callback:
                self.log_callback(f"数据库已有文章: {len(existing_urls)}篇")
            
            # 找出新文章
            new_entries = [
                entry for entry in feed.entries 
                if entry.link not in existing_urls
            ]
            
            if not new_entries:
                if self.status_callback:
                    self.status_callback("✓ 已是最新", False)
                if self.log_callback:
                    self.log_callback("✓ 没有新文章，已是最新")
                    self.log_callback("=== 更新完成 ===\n")
                return
            
            if self.log_callback:
                self.log_callback(f"\n发现{len(new_entries)}篇新文章:")
                for i, entry in enumerate(new_entries, 1):
                    self.log_callback(f"{i}. {entry.title}")
            
            if self.status_callback:
                self.status_callback(f"↻ 翻译{len(new_entries)}篇新文章...", False)
            if self.log_callback:
                self.log_callback("\n开始翻译新文章标题...")
            
            # 只翻译新文章的标题
            new_titles = [entry.title for entry in new_entries]
            translated_titles = self.translator.translate_batch(new_titles)
            
            if self.log_callback:
                self.log_callback("\n翻译结果:")
                for i, (title, translated) in enumerate(zip(new_titles, translated_titles), 1):
                    self.log_callback(f"{i}. {translated}")
                    self.log_callback(f"   原标题: {title}")
            
            if self.status_callback:
                self.status_callback("↻ 保存到数据库...", False)
            if self.log_callback:
                self.log_callback("\n正在保存到数据库...")
            
            # 准备新文章数据
            articles_data = []
            for entry, translated_title in zip(new_entries, translated_titles):
                article = Article(
                    id=None,
                    title=entry.title,
                    translated_title=translated_title,
                    url=entry.link,
                    source=url,
                    created_at=datetime.now(),
                    summary=None  # 初始化summary为None
                )
                articles_data.append(article)
            
            # 保存到数据库
            self.db.save_articles(articles_data)
            
            if self.status_callback:
                self.status_callback(f"✓ 已更新{len(new_entries)}篇", False)
            if self.log_callback:
                self.log_callback(f"\n✓ 成功更新{len(new_entries)}篇文章")
                self.log_callback("=== 更新完成 ===\n")
            
        except Exception as e:
            if self.status_callback:
                self.status_callback("✗ 同步失败", True)
            if self.log_callback:
                self.log_callback(f"✗ 后台更新过程出错: {str(e)}")
                self.log_callback("=== 更新失败 ===\n")

    def fetch_feed(self, url: str = config.DEFAULT_RSS_URL) -> None:
        """获取并解析RSS源"""
        # 首先从数据库获取现有文章
        db_articles = self.db.get_articles_by_source(url)
        self.articles = [(article.title, article.translated_title, article.url) 
                        for article in db_articles]
        
        # 启动后台更新线程
        update_thread = threading.Thread(
            target=self.update_feed_worker,
            args=(url,)
        )
        update_thread.daemon = True  # 设置为守护线程，主程序退出时自动结束
        update_thread.start()
        
        if not self.articles:
            # 等待后台更新完成第一批数据
            time.sleep(2)  # 给后台线程一些时间来获取和处理数据
            db_articles = self.db.get_articles_by_source(url)
            self.articles = [(article.title, article.translated_title, article.url) 
                           for article in db_articles]

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