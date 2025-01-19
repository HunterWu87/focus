"""数据库管理器"""
import psycopg2
from datetime import datetime
from typing import List, Optional
from .models import Article

class DatabaseManager:
    def __init__(self):
        """初始化数据库管理器"""
        self.conn_params = {
            "dbname": "postgres",  # 默认数据库
            "user": "postgres",
            "password": "260682",  # 请根据您的设置修改
            "host": "localhost",
            "port": "2606"
        }
        self.init_database()

    def init_database(self):
        """初始化数据库和表"""
        # 连接到默认数据库
        conn = psycopg2.connect(**self.conn_params)
        conn.autocommit = True  # 设置自动提交
        try:
            with conn.cursor() as cur:
                # 检查rss_articles数据库是否存在
                cur.execute("SELECT 1 FROM pg_database WHERE datname='rss_articles'")
                if not cur.fetchone():
                    # 创建数据库
                    cur.execute("CREATE DATABASE rss_articles")
        finally:
            conn.close()

        # 更新连接参数到新数据库
        self.conn_params["dbname"] = "rss_articles"

        # 创建表和更新表结构
        conn = psycopg2.connect(**self.conn_params)
        try:
            with conn.cursor() as cur:
                # 创建表（如果不存在）
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS articles (
                        id SERIAL PRIMARY KEY,
                        title TEXT NOT NULL,
                        translated_title TEXT,
                        url TEXT UNIQUE NOT NULL,
                        source TEXT,
                        summary TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # 检查并添加summary字段
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name='articles' AND column_name='summary'
                """)
                if not cur.fetchone():
                    print("添加summary字段到articles表...")
                    cur.execute("""
                        ALTER TABLE articles 
                        ADD COLUMN summary TEXT
                    """)
                
                # 创建URL唯一索引以实现去重
                cur.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_articles_url 
                    ON articles(url)
                """)
                conn.commit()
        finally:
            conn.close()

    def save_articles(self, articles: List[Article]) -> None:
        """
        保存文章列表，自动去重
        
        Args:
            articles: 文章对象列表
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                for article in articles:
                    try:
                        cur.execute("""
                            INSERT INTO articles (title, translated_title, url, source, summary, created_at)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON CONFLICT (url) DO UPDATE 
                            SET translated_title = EXCLUDED.translated_title,
                                title = EXCLUDED.title,
                                source = EXCLUDED.source,
                                summary = EXCLUDED.summary,
                                created_at = EXCLUDED.created_at
                        """, (
                            article.title,
                            article.translated_title,
                            article.url,
                            article.source,
                            article.summary,
                            article.created_at
                        ))
                    except Exception as e:
                        print(f"保存文章时出错: {str(e)}")
                        continue
                conn.commit()

    def get_articles(self, limit: int = 50) -> List[Article]:
        """
        获取最近的文章列表
        
        Args:
            limit: 返回的最大文章数量
            
        Returns:
            List[Article]: 文章对象列表
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, translated_title, url, source, created_at
                    FROM articles
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (limit,))
                
                return [
                    Article(
                        id=row[0],
                        title=row[1],
                        translated_title=row[2],
                        url=row[3],
                        source=row[4],
                        created_at=row[5]
                    )
                    for row in cur.fetchall()
                ]

    def get_article_summary(self, url: str) -> Optional[str]:
        """
        获取文章总结
        
        Args:
            url: 文章URL
            
        Returns:
            Optional[str]: 文章总结，如果不存在则返回None
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT summary
                    FROM articles
                    WHERE url = %s
                """, (url,))
                
                row = cur.fetchone()
                return row[0] if row else None

    def get_article_by_url(self, url: str) -> Optional[Article]:
        """
        通过URL获取文章
        
        Args:
            url: 文章URL
            
        Returns:
            Optional[Article]: 文章对象，如果不存在则返回None
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, translated_title, url, source, created_at, summary
                    FROM articles
                    WHERE url = %s
                """, (url,))
                
                row = cur.fetchone()
                if row:
                    return Article(
                        id=row[0],
                        title=row[1],
                        translated_title=row[2],
                        url=row[3],
                        source=row[4],
                        created_at=row[5],
                        summary=row[6]
                    )
                return None

    def get_articles_by_source(self, source: str, limit: int = 50) -> List[Article]:
        """
        获取指定源的最近文章列表
        
        Args:
            source: RSS源URL
            limit: 返回的最大文章数量
            
        Returns:
            List[Article]: 文章对象列表
        """
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, title, translated_title, url, source, created_at
                    FROM articles
                    WHERE source = %s
                    ORDER BY created_at DESC
                    LIMIT %s
                """, (source, limit))
                
                return [
                    Article(
                        id=row[0],
                        title=row[1],
                        translated_title=row[2],
                        url=row[3],
                        source=row[4],
                        created_at=row[5]
                    )
                    for row in cur.fetchall()
                ]

    def update_article_summary(self, url: str, summary: str) -> None:
        """更新文章总结"""
        print("\n=== 保存文章总结到数据库 ===")
        print(f"文章URL: {url}")
        print("正在保存...")
        
        with psycopg2.connect(**self.conn_params) as conn:
            with conn.cursor() as cur:
                try:
                    cur.execute("""
                        UPDATE articles 
                        SET summary = %s
                        WHERE url = %s
                    """, (summary, url))
                    conn.commit()
                    print("✓ 总结保存成功")
                except Exception as e:
                    print(f"✗ 更新文章总结时出错: {str(e)}")
        print("=== 保存完成 ===\n") 