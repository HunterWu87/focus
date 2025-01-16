"""主程序入口"""
from src.rss_translator.translator import TranslationService
from src.rss_translator.rss_reader import RSSReader

def main():
    try:
        # 初始化服务
        translator = TranslationService()
        reader = RSSReader(translator)
        
        # 获取并显示RSS内容
        reader.fetch_feed()
        
        # 启动交互模式
        reader.interactive_mode()
        
    except Exception as e:
        print(f'程序错误: {str(e)}')

if __name__ == '__main__':
    main() 