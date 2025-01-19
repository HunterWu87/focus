"""主程序入口"""
from src.rss_translator.ui import RSSTranslatorUI

def main():
    app = RSSTranslatorUI()
    app.run()

if __name__ == '__main__':
    main() 