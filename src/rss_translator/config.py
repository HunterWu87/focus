"""配置文件，存储所有配置项"""
import os
from dotenv import load_dotenv

# 加载.env文件中的环境变量
load_dotenv()

# 版本信息
APP_VERSION = "0.1.0"
MODEL_NAME = "deepseek-chat"
MODEL_VERSION = "DeepSeek-V3"  # DeepSeek Chat已全面升级为V3版本

# API配置
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    raise ValueError("请设置DEEPSEEK_API_KEY环境变量")

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"

# RSS配置
DEFAULT_RSS_URL = os.getenv('RSS_URL', "http://feeds.bbci.co.uk/news/rss.xml")

# 请求配置
REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '0.5'))  # API请求间隔时间（秒） 